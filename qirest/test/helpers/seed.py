#!/usr/bin/env python
import sys
import os
import re
import argparse
from datetime import (datetime, timedelta)
import pytz
import random
import math
from decimal import Decimal
from bunch import (Bunch, bunchify)
from mongoengine import connect
from qiutil import uid
from qiutil.file import splitexts
from qirest_client.helpers import database
from qirest_client.model.subject import (ImagingCollection, Subject)
from qirest_client.model.imaging import (
  Session, SessionDetail, Modeling, ModelingProtocol, Scan, ScanProtocol,
  Registration, RegistrationProtocol, LabelMap, Image, MultiImageResource,
  SingleImageResource
)
from qirest_client.model.common import TumorExtent
from qirest_client.model.clinical import (
  Treatment, Drug, Dosage, Biopsy, Surgery, PathologyReport, TNM,
  TumorLocation, BreastSurgery, BreastPathology, ResidualCancerBurden,
  HormoneReceptorStatus, BreastGeneticExpression, BreastNormalizedAssay,
  ModifiedBloomRichardsonGrade, SarcomaPathology, FNCLCCGrade,
  NecrosisPercentValue, NecrosisPercentRange, necrosis_percent_as_score
)
from qirest.server import settings

DEFAULT_PROJECT = 'QIN_Test'
"""The test/dev project name."""

CONNECT_SETTINGS = dict(
    db='MONGO_DBNAME',
    host='MONGO_HOST',
    port='MONGO_PORT',
    username='MONGO_USERNAME',
    password='MONGO_PASSWORD'
)
"""The connection {parameter: constant} dictionary."""


class Collection(object):
    def __init__(self, name, **opts):
        self.name = name
        self.options = bunchify(opts)
    
    def create_grade(self, **opts):
        raise NotImplementedError("Subclass responsibility")
    
    def create_tnm(self, **opts):
        # The tumor type-specific grade.
        grade = self.create_grade()
        
        # The tumor size.
        tumor_size_max = TNM.Size.tumor_size_choices(self.name)[-1]
        tumor_size = _random_int(1, tumor_size_max)
        suffix_choices = TNM.Size.suffix_choices(self.name)
        suffix_ndx = _random_int(-1, len(suffix_choices) - 1)
        if suffix_ndx < 0:
            suffix = None
        else:
            suffix = suffix_choices[suffix_ndx]
        size_content = dict(tumor_size=tumor_size)
        size_opts = {k: opts.pop(k) for k in TNM.Size._fields.iterkeys()
                     if k in opts}
        size_content.update(size_opts)
        size = TNM.Size(**size_content)
        
        # The remaining TNM fields.
        lymph_status_max = TNM.lymph_status_choices(self.name)[-1]
        lymph_status = _random_int(0, lymph_status_max)
        metastasis = _random_boolean()
        invasion = _random_boolean()
        
        # The TNM {attribute: value} dictionary.
        tnm_content = dict(tumor_type=self.name, grade=grade, size=size,
                           lymph_status=lymph_status, metastasis=metastasis,
                           lymphatic_vessel_invasion=invasion)
        # The options override the random values.
        tnm_content.update(opts)
        
        return TNM(**tnm_content)


class Breast(Collection):
    """
    The test Breast collection has four visits with 32 volumes each.
    """
    def __init__(self):
        super(Breast, self).__init__(
            name='Breast', description='QIN breast DCE MRI',
            url='https://wiki.cancerimagingarchive.net/display/Public/QIN+Breast+DCE-MRI',
            visit_count=4, volume_count=32
        )
    
    def create_grade(self):
        """
        :return: the ModifiedBloomRichardson grade
        """
        tubular_formation = _random_int(1, 3)
        nuclear_pleomorphism = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)
        
        return ModifiedBloomRichardsonGrade(tubular_formation=tubular_formation,
                                     nuclear_pleomorphism=nuclear_pleomorphism,
                                     mitotic_count=mitotic_count)
    
    def create_pathology(self, **opts):
        # The TNM.
        tnm_opts = dict(prefix='p')
        if 'tnm' in opts:
            tnm_opts.update(opts.pop('tnm'))
        tnm = self.create_tnm(**tnm_opts)
        
        # The tumor extent.
        length = _random_int(20, 25)
        width = _random_int(10, 20)
        depth = _random_int(5, 10)
        extent = TumorExtent(length=length, width=width, depth=depth)
        
        # The breast hormone status result.
        hr_opts = opts.pop('hormone_receptors', {})
        hormone_receptors = self._create_hormone_receptors(**hr_opts)
        
        # The gene expression result.
        gene_expr_opts = opts.pop('genetic_expression', {})
        # If this subject is estrogen receptor-status-positive
        # and has no lymph nodes, then create an assay.
        estrogen = next((hr for hr in hormone_receptors
                         if hr.hormone == 'estrogen'),
                        None)
        if estrogen and estrogen.positive and not tnm.lymph_status:
            assay_opts = opts.pop('normalized_assay', {})
            assay = self._create_normalized_assay(**assay_opts)
            gene_expr_opts['normalized_assay'] = assay
        genetic_expression = self._create_genetic_expression(**gene_expr_opts)
        
        # The {attribute: value} dictionary.
        values = dict(tnm=tnm, extent=extent,
                      hormone_receptors=hormone_receptors,
                      genetic_expression=genetic_expression)
        values.update(opts)
        
        return BreastPathology(**values)
    
    def _create_hormone_receptors(self, **opts):
        # The estrogen status.
        estrogen_opts = opts.get('estrogen', {})
        estrogen = self._create_hormone_status('estrogen', **estrogen_opts)
        # The progesterone status.
        progesterone_opts = opts.get('progesterone', {})
        progesterone = self._create_hormone_status('progesterone', **progesterone_opts)
        
        return [estrogen, progesterone]
    
    def create_rcb(self):
        return ResidualCancerBurden(
            tumor_cell_density=_random_int(0, 40),
            dcis_cell_density=_random_int(0, 20),
            positive_node_count=_random_int(0, 5),
            total_node_count=_random_int(0, 20),
            largest_nodal_metastasis_length=_random_int(0, 10)
        )
    
    def _create_genetic_expression(self, **opts):
        # HER2 NEU IHC is one of 0, 1, 2, 3.
        her2_neu_ihc = _random_int(0, 3)
        
        # HER2 NEU FISH is True (positive) or False (negative).
        her2_neu_fish = _random_boolean()
        
        # KI67 is a percent.
        ki67 = _random_int(0, 100)
        
        values = dict(her2_neu_ihc=her2_neu_ihc, her2_neu_fish=her2_neu_fish,
                      ki67=ki67)
        values.update(opts)
        
        return BreastGeneticExpression(**values)
    
    def _create_hormone_status(self, hormone, **opts):
        # Make the default {attribute: value} dictionary.
        values = dict(
            hormone=hormone,
            positive =_random_boolean()
        )
        if values['positive']:
            values['quick_score'] = _random_int(0, 8),
            values['intensity'] = _random_int(0, 100)
        # Override the defaults.
        values.update(opts)
        
        # Return the new receptor status.
        return HormoneReceptorStatus(**values)
    
    def _create_normalized_assay(self, **opts):
        # Make the default {attribute: value} dictionary.
        gstm1 = _random_int(0, 15)
        cd68 = _random_int(0, 15)
        bag1 = _random_int(0, 15)
        her2 = self._create_HER2_group()
        estrogen = self._create_estrogen_group()
        proliferation = self._create_proliferation_group()
        invasion = self._create_invasion_group()
        groups = dict(her2=her2, estrogen=estrogen,
                      proliferation=proliferation, invasion=invasion)
        values = dict(gstm1=gstm1, cd68=cd68, bag1=bag1, **groups)
        # Override the defaults.
        values.update(opts)
        
        # Return the new assay.
        return BreastNormalizedAssay(**values)
    
    def _create_HER2_group(self):
        grb7 = _random_int(0, 15)
        her2 = _random_int(0, 15)
        
        return BreastNormalizedAssay.HER2(grb7=grb7, her2=her2)
    
    def _create_estrogen_group(self):
        er = _random_int(0, 15)
        pgr = _random_int(0, 15)
        bcl2 = _random_int(0, 15)
        scube2 = _random_int(0, 15)
        
        return BreastNormalizedAssay.Estrogen(er=er, pgr=pgr, bcl2=bcl2, scube2=scube2)
    
    def _create_proliferation_group(self):
        ki67 = _random_int(0, 15)
        stk15 = _random_int(0, 15)
        survivin = _random_int(0, 15)
        ccnb1 = _random_int(0, 15)
        mybl2 = _random_int(0, 15)
        
        return BreastNormalizedAssay.Proliferation(
            ki67=ki67, stk15=stk15, survivin=survivin, ccnb1=ccnb1, mybl2=mybl2
        )
    
    def _create_invasion_group(self):
        mmp11 = _random_int(0, 15)
        ctsl2 = _random_int(0, 15)
        
        return BreastNormalizedAssay.Invasion(mmp11=mmp11, ctsl2=ctsl2)


class Sarcoma(Collection):
    """
    The test Sarcoma collection has three visits with 40 volumes each.
    
    Note: the AIRC Sarcoma scan count and numbering scheme varies.
    """
    
    def __init__(self):
        super(Sarcoma, self).__init__(
            name='Sarcoma',
            description='QIN soft-tissue sarcoma DCE MRI',
            url='https://wiki.cancerimagingarchive.net/display/Public/QIN-SARCOMA',
            visit_count=3, volume_count=40
        )
    
    def create_grade(self):
        """
        Makes the Sarcoma FNCLCC grade object.
        The grade *necrosis_score* attribute is not set, since it
        is calculated later from the *necrosis_percent* attribute.
        
        :return: the FNCLCC grade
        """
        differentiation = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)
        
        return FNCLCCGrade(differentiation=differentiation,
                           mitotic_count=mitotic_count)
    
    def create_pathology(self, **opts):
        # The tumor site.
        location = TumorLocation(body_part='Thigh', sagittal_location='Left',
                                 coronal_location='Posterior')
        # The histology.
        histology = 'Fibrosarcoma'
        
        # The necrosis percent is either a value or a decile range.
        if _random_boolean():
            value = _random_int(0, 100)
            necrosis_percent = NecrosisPercentValue(value=value)
        else:
            low = _random_int(0, 9) * 10
            start = NecrosisPercentRange.LowerBound(value=low)
            stop = NecrosisPercentRange.UpperBound(value=low+10)
            necrosis_percent = NecrosisPercentRange(start=start, stop=stop)
        
        # The tumor extent.
        length = _random_int(20, 25)
        width = _random_int(10, 20)
        depth = _random_int(5, 10)
        extent = TumorExtent(length=length, width=width, depth=depth)
        
        # The TNM.
        tnm_opts = dict(prefix='p')
        if 'tnm' in opts:
            tnm_opts.update(opts.pop('tnm'))
            tnm_opts.update(necrosis_score=necrosis_score)
        tnm = self.create_tnm(**tnm_opts)
        # Calculate the necrosis score.
        tnm.grade.necrosis_score = necrosis_percent_as_score(necrosis_percent)
        values = dict(tnm=tnm, location=location, histology=histology,
                      extent=extent, necrosis_percent=necrosis_percent)
        values.update(opts)
        
        return SarcomaPathology(**values)


COLLECTIONS = [Breast(), Sarcoma()]


def collection_for(name):
    try:
        return next((coll for coll in COLLECTIONS if coll.name == name))
    except StopIteration:
        raise ValueError("The collection is not supported: %s" % name)


DATE_0 = datetime(2013, 1, 4, tzinfo=pytz.utc)
"""The first image acquisition date."""

FXL_K_TRANS_AVG = 0.2
"""The average Standard Model Ktrans value."""

DELTA_K_TRANS_FACTOR = 1.3
"""
The detal Ktrans multiplier.
The FXR (Shutter Speed Model) Ktrans = FXL_K_TRANS_AVG * DELTA_K_TRANS_FACTOR.
"""

TAU_I_0 = 0.4875
"""The first tau_i."""

V_E_0 = 0.6113
"""The first v_e vale."""

AVG_BOLUS_ARRIVAL_NDX = 2
"""Bolus arrivals are spread evenly around the third visit."""

REG_PARAMS = dict(
    transforms='[Rigid, Affine, SyN]',
    metric='[MI, MI, CC]',
    metric_weight='[1, 1, 1]',
    number_of_iterations='[[10000, 500, 200, 100], [10000, 500, 200, 100], [100, 20, 10]]',
    radius_or_number_of_bins='[32, 32, 4]',
    sampling_strategy='[Regular, Regular, None]',
    sampling_percentage='[0.3, 0.3, None]',
    smoothing_sigmas='[[3,2,1,0], [3,2,1,0], [2,1,0]]',
    shrink_factors='[[8,4,2,1], [8,4,2,1], [4,2,1]]',
    transform_parameters='[(0.1,), (0.1,), (0.1, 3, 0)]'
)

# The modeling R1 input parameters.
R1_PARAMS = dict(r1_0_val=0.7, baseline_end_idx=1)

PROTOCOLS = Bunch()
"""
The following protocols:
* bolero - the Bolero modeling protocol
* t1 - the T1 scan protocol
* t2 - the T2 scan protocol
* ants - the ANTS registration protocol

:Note: these protocols are added in the :meth:`seed` function.
"""


def seed(project=None):
    """
    Populates the currently connected MongoDB database with three
    subjects each of the :const:`COLLECTIONS`.
    
    :Note: existing content which matches the seed content, including
      imaging collection objects, subjects and subject detail, is
      deleted from the database first. Other database content is
      retained. Protocols are created on demand if no matching
      protocol is found.
    
    :param project: the name of the project to seed
        (default ``QIN_TEST``)
    :return: a list consisting of three *project* subjects for
        each collection in :const:`COLLECTIONS`
    """
    if not project:
        project = DEFAULT_PROJECT
    # Clear out the old content, if any.
    clear(project)
    # Initialize the pseudo-random generator.
    random.seed()
    # Make the protocols.
    PROTOCOLS.update(_create_protocols())
    # Make the subjects.
    # Note: itertools chain on a generator is preferable to iterate over
    # the collections. This works in python 1.7.1, but not python 1.7.2.
    # The work-around is to build up the subject collection in the for
    # loop below.
    coll_sbjs = []
    for coll in COLLECTIONS:
        coll_sbjs.extend(_seed_collection(project, coll))
    
    return coll_sbjs


def mock_clinical(project):
    """
    Populates the currently connected MongoDB database subjects with
    clinical data.
    """
    # Initialize the pseudo-random generator.
    random.seed()
    # The existing subjects.
    sbjs = Subject.objects(project=project)
    for sbj in sbjs:
        # Clear the existing clinical data.
        cln = list(sbj.clinical_encounters)
        if cln:
            sbj.encounters = list(sbj.sessions)
        # Add the new clinical data.
        _add_mock_clinical(sbj)
        sbj.save()


def clear(project):
    """Removes the seeded documents."""
    for coll in COLLECTIONS:
        _clear_collection(project, coll.name)


def _seed_collection(project, collection):
    # Make the collection database object.
    opts = {attr: val for attr, val in collection.options.iteritems()
            if attr in ImagingCollection._fields}
    coll = ImagingCollection(project=project,
                             name=collection.name,
                             **opts)
    coll.save()
    # Make and return the subjects.
    return [_seed_subject(project, collection, sbj_nbr)
            for sbj_nbr in range(1, 4)]


def _clear_collection(project, collection):
    for sbj_nbr in range(1, 4):
        try:
            sbj = Subject.objects.get(number=sbj_nbr, project=project,
                                      collection=collection)
            sbj.delete()
        except Subject.DoesNotExist:
            pass
    try:
        coll = ImagingCollection.objects.get(name=collection)
        coll.delete()
    except ImagingCollection.DoesNotExist:
        pass


def _seed_subject(project, collection, subject_number):
    """
    If the given subject is already in the database, then the
    subject is ignored. Otherwise, a new subject is created
    and populated with detail information.
    
    :param collection: the subject collection
    :param subject_number: the subject number
    :return: the subject with the given collection and number
    """
    try:
        sbj = Subject.objects.get(number=subject_number, project=project,
                                  collection=collection.name)
    except Subject.DoesNotExist:
        sbj = _create_subject(project, collection, subject_number)
    
    return sbj


ETHNICITY_INCIDENCE = [15, 85]
"""
The rough US ethnicity incidence for the respective ethnicity choices.
The incidences sum to 100.
"""

RACE_INCIDENCE = [70, 15, 5, 5, 5]
"""
The rough US race incidence for the respective race choices.
The incidences sum to 100.
"""

def _create_protocols():
    """Returns the protocols described in :const:`PROTOCOLS`."""
    # The modeling protocol.
    mdl_key = dict(technique='BOLERO', configuration=dict(r1=R1_PARAMS))
    bolero = database.get_or_create(ModelingProtocol, mdl_key)
    # The T1 scan protocol.
    t1 = database.get_or_create(ScanProtocol, dict(technique='T1'))
    # The T2 scan protocol.
    t2 = database.get_or_create(ScanProtocol, dict(technique='T2'))
    # The registration protocol.
    ants_cfg = {'Registration': REG_PARAMS}
    ants_key = dict(technique='ANTs', configuration=ants_cfg)
    ants = database.get_or_create(RegistrationProtocol, ants_key)
    
    return dict(t1=t1, t2=t2, bolero=bolero, ants=ants)


def _create_subject(project, collection, subject_number):
    # The subject with just a secondary key.
    subject = Subject(project=project, collection=collection.name,
                      number=subject_number)
    
    # Start with the MR sessions.
    subject.encounters = [_create_session(collection, subject, i + 1)
                          for i in range(collection.options.visit_count)]
    
    # Fabricate the clinical data.
    _add_mock_clinical(subject)
    
    # Save the subject.
    subject.save()
    
    return subject


def _add_mock_clinical(subject):
    """
    Adds clinical data to the given subject.
    
    :param subject: the subject to update
    """
    # The subject collection.
    collection = collection_for(subject.collection)
    # The imaging sessions.
    sessions = list(subject.sessions)

    # The patient demographics.
    yr = _random_int(1950, 1980)
    subject.birth_date = datetime(yr, 7, 7, tzinfo=pytz.utc)
    # Only show one race.
    subject.races = [_choose_race()]
    # The ethnicity is None half of the time.
    subject.ethnicity = _choose_ethnicity()
    # The gender is roughly split.
    subject.gender = _choose_gender(collection)
    
    # The neodjuvant treatment starts a few days after the first visit.
    offset = _random_int(0, 3)
    neo_rx_begin = sessions[0].date + timedelta(days=offset)
    # The neodjuvant treatment ends a few days before the last visit.
    offset = _random_int(0, 3)
    neo_rx_end = sessions[-1].date - timedelta(days=offset)
    neo_rx = Treatment(treatment_type='Neoadjuvant', start_date=neo_rx_begin,
                       end_date=neo_rx_end)
    
    # The sample seed Breast patients have neodjuvant drugs.
    if isinstance(collection, Breast):
        # trastuzumab.
        trast = Drug(name='trastuzumab')
        trast_amt = _random_float(20, 30)
        trast_dosage = Dosage(agent=trast, start_date=neo_rx_begin,
                              duration=14, amount=trast_amt)
        # pertuzumab.
        pert = Drug(name='pertuzumab')
        pert_amt = _random_float(40, 50)
        pert_dosage = Dosage(agent=pert, start_date=neo_rx_begin,
                             duration=14, amount=pert_amt)
        neo_rx.dosages = [trast_dosage, pert_dosage]
    
    # The primary treatment (surgery) is a few days after the last scan.
    offset = _random_int(0, 10)
    surgery_date = sessions[-1].date + timedelta(days=offset)
    primary_rx = Treatment(treatment_type='Primary', start_date=surgery_date,
                           end_date=surgery_date)
    
    # Adjuvant treatment begins shortly after surgery.
    offset = _random_int(0, 3)
    adj_rx_begin = surgery_date + timedelta(days=offset)
    # Adjuvant treatment ends about two weeks later.
    offset = _random_int(10, 20)
    adj_rx_end = adj_rx_begin + timedelta(days=offset)
    adj_rx = Treatment(treatment_type='Adjuvant', start_date=adj_rx_begin,
                       end_date=adj_rx_end)
    
    # Add the treatments.
    subject.treatments = [neo_rx, primary_rx, adj_rx]
    
    # The biopsy is a few days before the first visit.
    offset = _random_int(0, 10)
    biopsy_date = sessions[0].date - timedelta(days=offset)
    
    # Force the first breast patient to be free of lymph nodes,
    # since we want at least one patient with a normalized assay.
    opts = {}
    if isinstance(collection, Breast) and subject.number == 1:
        opts['hormone_receptors'] = dict(estrogen=dict(positive=True))
        opts['tnm'] = dict(lymph_status=0)
    # The biopsy has a pathology report.
    biopsy_tumor_path = collection.create_pathology(**opts)
    biopsy_path = PathologyReport(tumors=[biopsy_tumor_path])
    # The initial weight is between 40 and 80 kg.
    weight = _random_int(40, 80)
    biopsy = Biopsy(date=biopsy_date, weight=weight, pathology=biopsy_path)
    
    # The surgery has a pathology report.
    surgery_tumor_path = collection.create_pathology(**opts)
    # Only a breast resection pathology report measures the RCB.
    if isinstance(collection, Breast):
        surgery_tumor_path.rcb = collection.create_rcb()
    surgery_path = PathologyReport(tumors=[surgery_tumor_path])
    # The weight varies a bit from the initial weight with a bias
    # towards loss.
    weight += _random_int(-10, 5)
    # Breast surgery has a surgery type.
    if isinstance(collection, Breast):
        # The surgery type.
        srg_type_ndx = _random_int(0, len(BreastSurgery.TYPE_CHOICES) - 1)
        surgery_type = BreastSurgery.TYPE_CHOICES[srg_type_ndx]
        # The surgery object.
        surgery = BreastSurgery(date=surgery_date, weight=weight,
                                surgery_type=surgery_type,
                                pathology=surgery_path)
    else:
        surgery = Surgery(date=surgery_date, weight=weight,
                          pathology=surgery_path)
    
    # Set the encounters.
    subject.encounters = sessions + [biopsy, surgery]


def _choose_race():
    # Partition the race incidence from 1 to 100 and select the race by
    # partition.
    offset = _random_int(0, 99)
    n = 0
    for i, proportion in enumerate(RACE_INCIDENCE):
        n += proportion
        if offset < n:
            # The first item in the race tuple is the database value,
            # the second is the display value.
            return Subject.RACE_CHOICES[i][0]


def _choose_ethnicity():
    offset = _random_int(0, 99)
    n = 0
    for i, proportion in enumerate(ETHNICITY_INCIDENCE):
        n += proportion
        if offset < n:
            # The first item in the ethnicity tuple is the database value,
            # the second is the display value.
            return Subject.ETHNICITY_CHOICES[i][0]


def _choose_gender(collection):
    if collection.name == 'Breast':
        return 'Female'
    else:
        # Half of the sarcoma subjects are male, half female.
        index = _random_int(0, 1)
        return Subject.GENDER_CHOICES[index]


FXL_K_TRANS_FILE_NAME = 'fxl_k_trans.nii.gz'

FXR_K_TRANS_FILE_NAME = 'fxr_k_trans.nii.gz'

DELTA_K_TRANS_FILE_NAME = 'delta_k_trans.nii.gz'

V_E_FILE_NAME = 'v_e_trans.nii.gz'

TAU_I_FILE_NAME = 'tau_i_trans.nii.gz'

COLOR_TABLE_FILE_NAME = '/etc/jet_colors.txt'


def _create_session(collection, subject, session_number):
    """
    Returns a new Session object whose detail includes the following:
    * a T1 scan with a registration
    * a T2 scan
    * a modeling result for the registration
    """
    # Stagger the inter-session duration.
    date = _create_session_date(subject, session_number)
    # Make the session detail.
    detail = _create_session_detail(collection, subject, session_number)
    # Save the detail first, since it is not embedded and we need to
    # set the detail reference to make the session.
    detail.save()
    # The embedded session modeling objects.
    modelings = _create_modeling(subject, session_number)
    
    return Session(date=date, modelings=[modelings], detail=detail)


def _create_session_detail(collection, subject, session_number):
    """
    Returns a new SessionDetail object which includes the following:
    * a T1 scan with a registration
    * a T2 scan
    * a modeling result for the registration
    """
    # The bolus arrival.
    arv = int(round((0.5 - random.random()) * 4)) + AVG_BOLUS_ARRIVAL_NDX
    # Make the scans.
    t1 = _create_t1_scan(collection, subject, session_number, arv)
    t2 = _create_t2_scan(collection, subject, session_number)
    scans = [t1, t2]
    
    # Return the session detail.
    return SessionDetail(scans=scans)


def _create_modeling(subject, session_number):
    # The modeling resource name.
    resource = "pk_%s" % uid.generate_string_uid()
    
    # Add modeling parameters with a random offset.
    factor = 1 + ((random.random() - 0.5) * 0.4)
    fxl_k_trans_avg = FXL_K_TRANS_AVG * factor
    fxl_k_trans_label_map = _create_label_map(FXL_K_TRANS_FILE_NAME)
    fxl_k_trans_img = Image(name=FXL_K_TRANS_FILE_NAME,
                            metadata=dict(average_intensity=fxl_k_trans_avg))
    fxl_k_trans = Modeling.ParameterResult(image=fxl_k_trans_img,
                                           label_map=fxl_k_trans_label_map)
    
    factor = DELTA_K_TRANS_FACTOR + ((random.random() - 0.5) * 0.4)
    fxr_k_trans_avg = fxl_k_trans_avg * factor
    fxr_k_trans_label_map = _create_label_map(FXR_K_TRANS_FILE_NAME)
    fxr_k_trans_img = Image(name=FXR_K_TRANS_FILE_NAME,
                            metadata=dict(average_intensity=fxr_k_trans_avg))
    fxr_k_trans = Modeling.ParameterResult(image=fxr_k_trans_img,
                                           label_map=fxr_k_trans_label_map)
    
    delta_k_trans_avg = fxl_k_trans_avg - fxr_k_trans_avg
    delta_k_trans_label_map = _create_label_map(DELTA_K_TRANS_FILE_NAME)
    delta_k_trans_img = Image(name=DELTA_K_TRANS_FILE_NAME,
                            metadata=dict(average_intensity=delta_k_trans_avg))
    delta_k_trans = Modeling.ParameterResult(image=delta_k_trans_img,
                                             label_map=delta_k_trans_label_map)
    
    offset = (0.5 - random.random()) * 0.2
    v_e_avg = V_E_0 + offset
    v_e_label_map = _create_label_map(V_E_FILE_NAME)
    v_e_img = Image(name=V_E_FILE_NAME,
                    metadata=dict(average_intensity=v_e_avg))
    v_e = Modeling.ParameterResult(image=v_e_img,
                                   label_map=v_e_label_map)
    
    offset = (0.5 - random.random()) * 0.2
    tau_i_avg = TAU_I_0 + offset
    tau_i_label_map = _create_label_map(TAU_I_FILE_NAME)
    tau_i_img = Image(name=TAU_I_FILE_NAME,
                      metadata=dict(average_intensity=tau_i_avg))
    tau_i = Modeling.ParameterResult(image=tau_i_img,
                                     label_map=tau_i_label_map)
    
    result = dict(fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                  delta_k_trans=delta_k_trans, v_e=v_e, tau_i=tau_i)
    
    return Modeling(protocol=PROTOCOLS.bolero,
                    source=Modeling.Source(registration=PROTOCOLS.ants),
                    resource=resource, result=result)


SESSION_OFFSET_RANGES = dict(
    Breast=[(0, 5), (10, 15), (25, 30), (50,60)],
    Sarcoma=[(0, 5), (10, 20), (40,50)]
)
"""The range of offsets from the initial date for the breast scan dates. """


def _create_session_date(subject, session_number):
    date_range = SESSION_OFFSET_RANGES[subject.collection][session_number - 1]
    offset = _random_int(*date_range)
    return DATE_0 + timedelta(days=offset)


def _create_t1_scan(collection, subject, session_number, bolus_arrival_index):
    # The number of test volumes to create.
    vol_cnt = collection.options.volume_count
    # Make the volume image filenames.
    filenames = [_volume_basename(i+1) for i in range(vol_cnt)]
    # Make the average intensity values.
    intensities = _create_intensities(vol_cnt, bolus_arrival_index)
    # Add a motion artifact.
    _add_motion_artifact(intensities)
    # Make the volume images.
    scan_images = [Image(name=filenames[i],
                         metadata=dict(average_intensity=intensities[i]))
                   for i in range(vol_cnt)]
    volumes = MultiImageResource(name='NIFTI', images=scan_images)
    
    # The time series.
    ts_image = Image(name='scan_ts.nii.gz')
    time_series = SingleImageResource(name='scan_ts', image=ts_image)
    
    # Make the T1 registration.
    reg = _create_registration(collection, subject, session_number,
                               bolus_arrival_index)
    
    return Scan(number=1, protocol=PROTOCOLS.t1, volumes=volumes,
                time_series=time_series, registrations=[reg],
                bolus_arrival_index=bolus_arrival_index)


def _create_t2_scan(collection, subject, session_number):
    # Make the volume image base name.
    filename = _volume_basename(1)
    image = Image(name=filename)
    # Make the volumes singleton.
    volumes = MultiImageResource(name='NIFTI', images=[image])
    
    return Scan(number=2, protocol=PROTOCOLS.t2, volumes=volumes)


def _create_registration(collection, subject, session_number,
                         bolus_arrival_index):
    # The number of test volumes to create.
    vol_cnt = collection.options.volume_count
    # The XNAT resource name.
    resource = "reg_%s" % uid.generate_string_uid()
    # Make the volume image file base names.
    filenames = [_volume_basename(i+1) for i in range(vol_cnt)]
    # Make the average intensity values.
    intensities = _create_intensities(vol_cnt, bolus_arrival_index)
    # Make the 3D volume images.
    reg_images = [Image(name=filenames[i],
                        metadata=dict(average_intensity=intensities[i]))
                  for i in range(vol_cnt)]
    volumes = MultiImageResource(name=resource, images=reg_images)
    
    # The 4D time series.
    ts_basename = "%s_ts.nii.gz" % resource
    ts_image = Image(name=ts_basename)
    time_series = SingleImageResource(name=resource, image=ts_image)
    
    return Registration(protocol=PROTOCOLS.ants, volumes=volumes,
                        time_series=time_series)


VOLUME_BASENAME_TMPL = "volume%03d.nii.gz"

def _volume_basename(volume):
    """
    Creates the file base name for the given scan volume hierarchy. The
    base name is given by ``volume``*volume*``.nii.gz``, where *volume*
    is the zero-padded volume number, e.g. ``volume002.nii.gz``.
    
    :param subject: the Subject object
    :param session: the session number
    :param scan: the scan number
    :param volume: the volume number
    """
    return VOLUME_BASENAME_TMPL % volume


def _create_label_map(modeling_file):
    base, ext = splitexts(modeling_file)
    label_map = base + '_color' + ext
    
    return LabelMap(name=label_map, color_table=COLOR_TABLE_FILE_NAME)


def _create_intensities(count, bolus_arrival_index):
    """
    :param count: the number of time points
    :param bolus_arrival_index: the bolus arrival volume index
    :return: the intensities array
    """
    # Ramp intensity up logarithmically (+ or - up to 5) until two time
    # points after bolus arrival.
    top = bolus_arrival_index + 2
    intensities = [(math.log(i + 1) * 20) + (random.random() * 5)
                   for i in range(top + 1)]
    top_intensity = intensities[top]
    
    # Tail intensity off inverse exponentially thereafter.
    for i in range(count - top - 1):
        # A negative exponential declining factor.
        factor = math.exp(-2 * (float(i + 1)/25))
        # The signal intensity.
        intensity = (factor * top_intensity) + (random.random() * 5)
        intensities.append(intensity)
    
    return intensities


def _add_motion_artifact(intensities):
    """
    Introduces a blip in the given intensity values. Five intensity values
    roughly halfway into the sequence are skewed slightly downward.
    
    :param intensities: the intensity values
    """
    start = int(len(intensities) / 2) + _random_int(-2, 2)
    for i in range(start, start + 5):
        intensities[i] -= random.random() * 8


def _random_int(low, high):
    """
    :param low: the inclusive minimum value
    :param high: the inclusive maximum value
    :return: a random integer in the inclusive [low, high] range
    """
    return int(_random_float(low, high))


def _random_float(low, high):
    """
    :param low: the inclusive minimum value
    :param high: the inclusive maximum value
    :return: a random float in the inclusive [low, high] range
    """
    return (random.random() * (high - low)) + low


def _random_boolean():
    """
    :return: a random True or False value
    """
    if _random_int(0, 1):
        return True
    else:
        return False


def _connect():
    """
    Connects to the Eve server with keywords obtained from the
    server settings. The connect keyword parameters consist of
    the :const:`CONNECT_SETTINGS` item keys whose item value is
    defined as a constant in the :mod:`qirest.server.settings`.
    The keyword parameter values are the corresponding settings
    constant value.
    """
    # The Eve connection parameters.
    kwargs = {attr: getattr(settings, const)
              for attr, const in CONNECT_SETTINGS.iteritems()
              if hasattr(settings, const)}
    # Connect to the database.
    connect(**kwargs)


def main(argv=sys.argv):
    # Parse the command line arguments.
    opts = _parse_arguments()
    # Connect to the database.
    _connect()
    # The project name.
    project = opts.get('project', DEFAULT_PROJECT)
    # If the clinical flag is set, then only add clinical data.
    # Otherwise, create new subjects with imaging and clinical data.
    if opts.get('clinical'):
        mock_clinical(project)
    else:
        seed(project)


def _parse_arguments():
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser()
    env_grp = parser.add_mutually_exclusive_group()
    env_grp.add_argument('--clinical', action='store_true',
                         help="Add mock clinical data to existing subjects")
    env_grp.add_argument('--project', help="the project to seed (default QIN_TEST)")

    args = vars(parser.parse_args())
    nonempty_args = dict((k, v) for k, v in args.iteritems() if v != None)

    return nonempty_args


if __name__ == "__main__":
    sys.exit(main())
