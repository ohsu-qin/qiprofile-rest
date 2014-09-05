#!/usr/bin/env python
import os
from datetime import (datetime, timedelta)
import pytz
import random
import math
from decimal import Decimal
from mongoengine import connect
from qiprofile_rest import choices
from qiprofile_rest.models import (Subject, SubjectDetail, Session, SessionDetail,
                                   Modeling, Series, Scan, Registration, Intensity,
                                   Probe,  Treatment, Encounter, BreastPathology,
                                   SarcomaPathology, TNM, NottinghamGrade, FNCLCCGrade,
                                   NecrosisPercentValue, NecrosisPercentRange,
                                   HormoneReceptorStatus)

PROJECT = 'QIN_Test'

COLLECTIONS = ['Breast', 'Sarcoma']

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
    algorithm='ANTS',
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

def seed():
    """
    Populates the MongoDB database named ``qiprofile_test`` with
    three subjects each of the ``Breast`` and ``Sarcoma`` collection.
    
    Note: existing subjects are not modified. In order to refresh the
    seed subjects, drop the ``qiprofile_test`` database first.
    
    
    @return: three :obj:`PROJECT` subjects for each collection in
        :obj:`COLLECTIONS`
    """
    # Initialize the pseudo-random generator.
    random.seed()
    # Make the subjects.
    # Note: itertools chain on a generator is preferable to iterate over
    # the collections. This works in python 1.7.1, but not python 1.7.2.
    # The work-around is to build up the subject collection in the for
    # loop below.
    coll_sbjs = []
    for coll in COLLECTIONS:
        coll_sbjs.extend(_seed_collection(coll))

    return coll_sbjs


def clear():
    """Removes the seeded documents."""
    for coll in COLLECTIONS:
        _clear_collection(coll)


def _seed_collection(collection):
    return [_seed_subject(collection, sbj_nbr)
            for sbj_nbr in range(1, 4)]


def _clear_collection(collection):
    for sbj_nbr in range(1, 4):
        try:
            sbj = Subject.objects.get(number=sbj_nbr, project=PROJECT,
                                      collection=collection)
            sbj.delete()
        except Subject.DoesNotExist:
            pass


def _seed_subject(collection, subject_number):
    """
    If the given subject is already in the database, then the
    subject is ignored. Otherwise, a new subject is created
    and populated with detail information.

    @param collection: the subject collection name
    @param subject_number: the subject number
    @return: the subject with the given collection and number
    """
    try:
        sbj = Subject.objects.get(number=subject_number, project=PROJECT,
                                  collection=collection)
    except Subject.DoesNotExist:
        sbj = _create_subject(collection, subject_number)

    return sbj


def _create_subject(collection, subject_number):
    subject = Subject(number=subject_number, project=PROJECT,
                      collection=collection)
    detail = _create_subject_detail(subject)
    detail.save()
    subject.detail = detail
    subject.save()

    return subject


def _create_subject_detail(subject):
    # The patient demographics.
    yr = int(40 * random.random()) + 1950
    birth_date = datetime(yr, 7, 7, tzinfo=pytz.utc)
    races = [choices.RACE_CHOICES[int(len(choices.RACE_CHOICES) * random.random())][0]]

    # Make the sessions.
    sessions = [_create_session(subject, sess_nbr) for sess_nbr in range(1, 5)]

    # The biopsy is after the first visit.
    offset = int(random.random() * 30)
    biopsy_date = sessions[0].acquisition_date + timedelta(days=offset)
    
    # The biopsy has a pathology report.
    biopsy_path = _create_pathology(subject.collection)
    biopsy = Encounter(encounter_type='Biopsy', date=biopsy_date, outcomes=[biopsy_path])

    # The surgery is after the penultimate visit.
    offset = int(random.random() * 30)
    surgery_date = sessions[-2].acquisition_date + timedelta(days=offset)
    # The surgery doesn't have an outcome.
    surgery = Encounter(encounter_type='Surgery', date=surgery_date)

    # The post-surgery assessment.
    offset = 3 + int(random.random() * 20)
    assessment_date = surgery_date + timedelta(days=offset)
    # The post-surgery assessment has a TNM.
    assessment_tnm = _create_tnm(subject.collection)
    assessment = Encounter(encounter_type='Assessment', date=assessment_date,
                           outcomes=[assessment_tnm])
    encounters = [biopsy, surgery, assessment]

    # The treatments.
    offset = 20 + int(random.random() * 10)
    neo_tx_begin = surgery_date - timedelta(days=offset)
    offset = int(random.random() * 10)
    neo_tx_end = surgery_date - timedelta(days=offset)
    neo_tx = Treatment(treatment_type='Neoadjuvant', begin_date=neo_tx_begin,
                           end_date=neo_tx_end)
    primary_tx = Treatment(treatment_type='Primary', begin_date=surgery_date,
                           end_date=surgery_date)
    offset = int(random.random() * 10)
    adj_tx_begin = surgery_date + timedelta(days=offset)
    offset = int(random.random() * 20)
    adj_tx_end = adj_tx_begin + timedelta(days=offset)
    adj_tx = Treatment(treatment_type='Adjuvant', begin_date=adj_tx_begin,
                       end_date=adj_tx_end)
    treatments = [neo_tx, primary_tx, adj_tx]

    # Make the subject detail.
    return SubjectDetail(birth_date=birth_date, races=races, encounters=encounters,
                         treatments=treatments, sessions=sessions)


def _create_pathology(collection):
    if collection == 'Breast':
        return _create_breast_pathology()
    elif collection == 'Sarcoma':
        return _create_sarcoma_pathology()
    else:
        raise ValueError("Collection type not recognized: %s" % collection)


def _create_breast_pathology():
    # The TNM score.
    tnm = _create_tnm('Breast', 'p')

    # The estrogen status.
    positive = _random_boolean()
    quick_score = _random_int(0, 8)
    intensity = _random_int(0, 100)
    estrogen = HormoneReceptorStatus(positive=positive,
                                     quick_score=quick_score,
                                     intensity=intensity)

    # The progestrogen status.
    positive = _random_boolean()
    quick_score = _random_int(0, 8)
    intensity = _random_int(0, 100)
    progestrogen = HormoneReceptorStatus(positive=positive,
                                         quick_score=quick_score,
                                         intensity=intensity)

    # HER2 NEU IHC is one of 0, 1, 2, 3.
    her2_neu_ihc = _random_int(0, 3)

    # HER2 NEU FISH is True (positive) or False (negative).
    her2_neu_fish = _random_boolean()

    # KI67 is a percent.
    ki_67 = _random_int(0, 100)

    return BreastPathology(tnm=tnm, estrogen=estrogen,
                           progestrogen=progestrogen,
                           her2_neu_ihc=her2_neu_ihc,
                           her2_neu_fish=her2_neu_fish,
                           ki_67=ki_67)


def _create_sarcoma_pathology():
    # The TNM score.
    tnm = _create_tnm('Sarcoma', 'p')

    # The tumor site.
    site = 'Thigh'

    # The necrosis percent is either a value or a decile range.
    if _random_boolean():
        value = _random_int(0, 100)
        necrosis_pct = NecrosisPercentValue(value=value)
    else:
        low = _random_int(0, 9) * 10
        start = NecrosisPercentRange.LowerBound(value=low)
        stop = NecrosisPercentRange.UpperBound(value=low+10)
        necrosis_pct = NecrosisPercentRange(start=start, stop=stop)

    # The histology                                      
    histology = 'Fibrosarcoma'

    return SarcomaPathology(tnm=tnm, site=site, necrosis_pct=necrosis_pct,
                            histology=histology)


def _create_tnm(collection, prefix=None):
    if collection == 'Breast':
        grade = _create_breast_grade()
    elif collection == 'Sarcoma':
        grade = _create_sarcoma_grade()
    else:
        raise ValueError("Collection type not recognized: %s" % collection)
    
    tumor_size_max = TNM.Size.tumor_size_choices(collection)[-1]
    tumor_size = _random_int(1, tumor_size_max)
    suffix_choices = TNM.Size.suffix_choices(collection)
    suffix_ndx = _random_int(-1, len(suffix_choices) - 1)
    if suffix_ndx < 0:
        suffix = None
    else:
        suffix = suffix_choices[suffix_ndx]
    size = TNM.Size(prefix=prefix, tumor_size=tumor_size, suffix=suffix)
    lymph_status_max = TNM.lymph_status_choices(collection)[-1]
    lymph_status = _random_int(0, lymph_status_max)
    metastasis = _random_boolean()
    invasion = _random_boolean()

    return TNM(grade=grade, size=size, lymph_status=lymph_status,
               metastasis=metastasis, lymphatic_vessel_invasion=invasion)


def _create_breast_grade():
    """
    @return the Nottingham grade
    """
    tubular_formation = _random_int(1, 3)
    nuclear_pleomorphism = _random_int(1, 3)
    mitotic_count = _random_int(1, 3)

    return NottinghamGrade(tubular_formation=tubular_formation,
                                 nuclear_pleomorphism=nuclear_pleomorphism,
                                 mitotic_count=mitotic_count)


def _create_sarcoma_grade():
    """
    @return the FNCLCC grade
    """
    differentiation = _random_int(1, 3)
    mitotic_count = _random_int(1, 3)
    necrosis = _random_int(0, 2)

    return FNCLCCGrade(differentiation=differentiation, mitotic_count=mitotic_count,
                       necrosis=necrosis)


def _create_session(subject, session_number):
    # Stagger the inter-session duration.
    offset = ((session_number - 1) * 20) + int(random.random() * 10)
    date = DATE_0 + timedelta(days=offset)

    # The bolus arrival.
    arv = int(round((0.5 - random.random()) * 4)) + AVG_BOLUS_ARRIVAL_NDX
    # Make the series list.
    series = _create_all_series(subject.collection)
    # Make the scan.
    scan = _create_scan(subject, session_number, series, arv)
    # Make the registration.
    reg = _create_registration(subject, session_number, series, arv)
    # Make the session detail.
    detail = SessionDetail(bolus_arrival_index=arv, series=series, scan=scan,
                           registrations=[reg])
    # Save the detail.
    detail.save()

    # Add modeling parameters with a random offset.
    factor = 1 + ((random.random() - 0.5) * 0.4)
    fxl_k_trans = FXL_K_TRANS_AVG * factor
    factor = DELTA_K_TRANS_FACTOR + ((random.random() - 0.5) * 0.4)
    fxr_k_trans = fxl_k_trans * factor
    offset = (0.5 - random.random()) * 0.2
    v_e = V_E_0 + offset
    offset = (0.5 - random.random()) * 0.2
    tau_i = TAU_I_0 + offset
    name = "pk_%d" % (((subject.number - 1) * 3) + session_number)
    modeling = Modeling(name=name, image_container_name=reg.name,
                        fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                        v_e=v_e, tau_i=tau_i)

    return Session(number=session_number, acquisition_date=date,
                   modeling=[modeling], detail=detail)


BREAST_SERIES_NUMBERS = [7, 8] + [11 + 2*n for n in range(0, 30)]

SARCOMA_SERIES_NUMBERS = [10, 11] + [14 + 2*n for n in range(0, 43)] + [101 + 2*n for n in range(0, 10)]

SERIES_NUMBERS = dict(
    Breast=BREAST_SERIES_NUMBERS,
    Sarcoma=SARCOMA_SERIES_NUMBERS
)


def _create_all_series(collection):
    # @param collection the Breast or Sarcoma collection
    # @returns an array of series objects
    return [Series(number=number) for number in SERIES_NUMBERS[collection]]


def _create_scan(subject, session_number, series, bolus_arrival_index):
    files = _create_scan_filenames(subject, session_number, series)
    intensity = _create_intensity(len(series), bolus_arrival_index)
    # Add a motion artifact.
    start = 12 + _random_int(0, 5)
    for i in range(start, start + 5):
        intensity.intensities[i] -= random.random() * 8

    return Scan(files=files, intensity=intensity)


def _create_registration(subject, session_number, series, bolus_arrival_index):
    resource = "reg_%02d" % session_number
    files = _create_resource_filenames(subject, session_number, resource, series)
    intensity = _create_intensity(len(series), bolus_arrival_index)

    return Registration(name=resource, files=files, intensity=intensity,
                        parameters=REG_PARAMS)


def _create_scan_filenames(subject, session_number, series):
    # Creates the file names for the given session. The file is
    # name is given as:
    #
    #     ``data``/<project>/<subject>/<session>/``scan``/<number>/``series``<number>``.nii.gz``
    #
    # e.g.::
    #
    #     data/QIN_Test/Breast003/Session02/scan/2/series002.nii.gz
    # * data/QIN_Test/Sarcoma003/Session02/resource/reg_AuX4d/series027.nii.gz
    #
    # @param subject the parent subject
    # @param session_number the session number
    # @param series the series array
    # @return the file name array
    return [_scan_filename(subject, session_number, series.number)
            for series in series]


def _create_resource_filenames(subject, session_number, resource, series):
    # Creates the file names for the given resource. The file is
    # name is given as:
    #
    #     ``data``/<project>/<subject>/<session>/``resource``/<resource>/``series``<number>``.nii.gz``
    #
    # e.g.::
    #
    #     data/QIN_Test/Sarcoma003/Session02/resource/reg_AuX4d/series027.nii.gz
    #
    # @param subject the parent subject
    # @param session_number the session number
    # @param resource the resource name
    # @param series the series array
    # @return the file name array
    return [_resource_filename(subject, session_number, resource, series.number)
            for series in series]


SESSION_TMPL = "data/%s/arc001/%s%03d_Session%02d/"

FILE_TMPL = "series%03d.nii.gz"

SCAN_TMPL = SESSION_TMPL + "SCANS/%d/NIFTI/" + FILE_TMPL

RESOURCE_TMPL = SESSION_TMPL + "RESOURCES/%s/" + FILE_TMPL


def _scan_filename(subject, session_number, series_number):
    return SCAN_TMPL % (subject.project, subject.collection, subject.number,
                        session_number, series_number, series_number)


def _resource_filename(subject, session_number, resource, series_number):
    return RESOURCE_TMPL % (subject.project, subject.collection,
                            subject.number, session_number, resource, series_number)


def _create_intensity(count, bolus_arrival_index):
    """
    @param count the number of time points
    @param bolus_arrival_index the bolus arrival series index
    @return the Intensity object
    """
    # Ramp intensity up logarithmically until two time points after
    # bolus arrival.
    top = bolus_arrival_index + 2
    intensities = [(math.log(i) * 20) + (random.random() * 5)
                   for i in range(1, top + 2)]
    arv_intensity = intensities[top]
    # Tail intensity off inverse exponentially thereafter.
    for i in range(1, count - top):
        # A negative exponential declining factor.
        factor = math.exp(-2 * (float(i)/25))
        # The signal intensity.
        intensity = (factor * arv_intensity) + (random.random() * 5)
        intensities.append(intensity)

    return Intensity(intensities=intensities)


def _random_int(low, high):
    """
    @param low the inclusive minimum value
    @param high the inclusive maximum value
    @return a random integer in the inclusive [low, high] range
    """
    return int(Decimal(random.random() * (high - low)).to_integral_value()) + low


def _random_boolean():
    """
    @return a random True or False value
    """
    if _random_int(0, 1):
        return True
    else:
        return False


if __name__ == "__main__":
    connect(db='qiprofile_test')
    seed()
