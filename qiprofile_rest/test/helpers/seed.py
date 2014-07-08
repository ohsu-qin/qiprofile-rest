#!/usr/bin/env python
import os
import datetime
import pytz
import random
import math

# Set the settings environment variable before loading the models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qiprofile_rest.settings')

from qiprofile_rest import choices
from qiprofile_rest.models import (Subject, SubjectDetail, Session, SessionDetail,
                                   Modeling, Series, Scan, Registration, Intensity,
                                   Probe,  Encounter, BreastPathology, TNM,
                                   NottinghamGrade, HormoneReceptorStatus)

PROJECT = 'QIN_Test'

COLLECTIONS = ['Breast', 'Sarcoma']

DATE_0 = datetime.datetime(2013, 1, 4, tzinfo=pytz.utc)
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
    :Note: this is a destructive operation. Existing objects are deleted
    from the database.

    @return: three :obj:`PROJECT` subjects for each collection in
        :obj:`COLLECTIONS`
    """
    # Initialize the pseudo-random generator.
    random.seed()
    # Make the subjects.
    # Note: itertools chain on a generator iterates over
    # the collections in python 1.7.1, but not python 1.7.2.
    # The work-around is to build the subject collection
    # in the for loop below.
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
    sbj = Subject(number=subject_number, project=PROJECT,
                collection=collection)
    detail = _create_subject_detail(sbj)
    detail.save()
    sbj.detail = detail
    sbj.save()

    return sbj


def _create_subject_detail(subject):
    # The patient demographics.
    yr = int(40 * random.random()) + 1950
    birth_date = datetime.datetime(yr, 7, 7, tzinfo=pytz.utc)
    races = [choices.RACE_CHOICES[int(len(choices.RACE_CHOICES) * random.random())][0]]

    # The biopsy encounter.
    biopsy_date = DATE_0.replace(year=2012, month=10)
    biopsy_path = _create_pathology()
    biopsy = Encounter(encounter_type='Biopsy', date=biopsy_date, outcome=biopsy_path)

    # The post-treatment encounter.
    post_treatment_date = DATE_0.replace(month=5)
    post_treatment_tnm = _create_tnm()
    post_treatment = Encounter(encounter_type='Assessment', date=post_treatment_date,
                               outcome=post_treatment_tnm)

    encounters = [biopsy, post_treatment]

    # Make the sessions.
    sessions = [_create_session(subject, sess_nbr) for sess_nbr in range(1, 5)]

    # Make the subject detail.
    return SubjectDetail(birth_date=birth_date, races=races, encounters=encounters,
                         sessions=sessions)


def _create_pathology():
    # The TNM score.
    tnm = _create_tnm()

    # The Nottingham grade.
    tubular_formation = int(random.random() * 4) + 1
    nuclear_pleomorphism = int(random.random() * 4) + 1
    mitotic_count = int(random.random() * 4) + 1
    nottingham = NottinghamGrade(tubular_formation=tubular_formation,
                                 nuclear_pleomorphism=nuclear_pleomorphism,
                                 mitotic_count=mitotic_count)

    # The estrogen status.
    quick_score = int(random.random() * 10)
    intensity = int(random.random() * 100)
    estrogen = HormoneReceptorStatus(positive=True, quick_score=quick_score,
                                     intensity=intensity)

    # The progestrogen status.
    quick_score = int(random.random() * 10)
    intensity = int(random.random() * 100)
    progestrogen = HormoneReceptorStatus(positive=True, quick_score=quick_score,
                                     intensity=intensity)

    # The pathogy findings.
    her2_neu_ihc = int(random.random() * 5)
    ki_67 = int(random.random() * 100)

    return BreastPathology(tnm=tnm, grade=nottingham, estrogen=estrogen,
                           progestrogen=progestrogen, her2_neu_ihc=her2_neu_ihc,
                           her2_neu_fish=True, ki_67=ki_67)


def _create_tnm():
    tnm_grade = int(random.random() * 3) + 2
    size = "pT%s" % tnm_grade
    lymph_status = int(random.random() * 5)
    return TNM(grade=tnm_grade, size=size, lymph_status=lymph_status, metastasis=False)


def _create_session(subject, session_number):
    # Bump the session month.
    mo = subject.number * session_number
    # Stagger the inter-session duration.
    day = DATE_0.day + ((session_number - 1) * 5)
    date = DATE_0.replace(month=mo, day=day)

    # The bolus arrival.
    arv = round((0.5 - random.random()) * 4) + AVG_BOLUS_ARRIVAL_NDX

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
    modeling = Modeling(name=name, fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                        v_e=v_e, tau_i=tau_i)

    # Make the series list.
    series = _create_all_series()

    # Make the scan.
    scan = _create_scan(subject, session_number)

    # Make the registration.
    registration = _create_registration(subject, session_number)

    # Make the session detail.
    sess_dtl = SessionDetail(bolus_arrival_index=arv, series=series, scan=scan,
                             registrations=[registration])

    # Save the detail.
    sess_dtl.save()

    return Session(number=session_number, acquisition_date=date,
                   modeling=modeling, detail=sess_dtl)


def _create_all_series():
    # @returns an array of 32 Series objects with numbers 7, 9, ...
    return [Series(number=7 + (2 * i)) for i in range(0,32)]


def _create_scan(subject, session_number):
    files = _files_for(subject, session_number)
    intensity = _create_intensity()
    # Add a motion artifact.
    start = 12 + int(random.random() * 5)
    for i in range(start, start + 5):
        intensity.intensities[i] -= random.random() * 8

    return Scan(files=files, intensity=intensity)


def _create_registration(subject, session_number):
    resource = "reg_%02d" % session_number
    files = _files_for(subject, session_number, resource)
    intensity = _create_intensity()

    return Registration(name=resource, files=files, intensity=intensity,
                        parameters=REG_PARAMS)


def _files_for(subject, session_number, resource=None):
    # Creates the test file names. If there is a resource, then
    # the image file container is that resource. Otherwise, the
    # the image file container is ``scan``.
    #
    # Examples:
    # * data/QIN_Test/Breast003/Session02/scan/2/series02.nii.gz
    # * data/QIN_Test/Sarcoma003/Session02/resource/reg_AuX4d/series27.nii.gz
    #
    # @return an array of 32 file names
    if resource:
        create_filename = lambda time_point: _resource_filename(subject, session_number, resource, time_point)
    else:
        create_filename = lambda time_point: _scan_filename(subject, session_number, time_point)

    return [create_filename(time_point) for time_point in range(1,33)]

SESSION_TMPL = "data/%s/%s%03d/Session%02d/"
FILE_TMPL = "series%02d.nii.gz"
SCAN_TMPL = SESSION_TMPL + "scan/%d/" + FILE_TMPL
RESOURCE_TMPL = SESSION_TMPL + "resource/%s/" + FILE_TMPL

def _scan_filename(subject, session_number, time_point):
    return SCAN_TMPL % (subject.project, subject.collection, subject.number,
                        session_number, time_point, time_point)

def _resource_filename(subject, session_number, resource, time_point):
    return RESOURCE_TMPL % (subject.project, subject.collection,
                            subject.number, session_number, resource, time_point)


def _create_intensity():
    # Ramp intensity up logarithmically until bolus arrival.
    intensities = [(math.log(i) * 20) + (random.random() * 5) 
                   for i in range(1, 7)]
    arv_intensity = intensities[5]
    # Tail intensity off inverse exponentially thereafter.
    for i in range(1, 27):
        # A negative exponential declining factor.
        factor = math.exp(-2 * (float(i)/25))
        # The signal intensity.
        intensity = (factor * arv_intensity) + (random.random() * 5)
        intensities.append(intensity)

    return Intensity(intensities=intensities)

if __name__ == "__main__":
    seed()
