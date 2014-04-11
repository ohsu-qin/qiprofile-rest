#!/usr/bin/env python
import os
import datetime
import pytz
import random
import math
from itertools import chain

# Set the settings environment variable before loading the models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qiprofile_rest.settings')

from qiprofile_rest import choices
from qiprofile_rest.models import (Subject, SubjectDetail, Session, SessionDetail,
                                   Modeling, Scan, Reconstruction, Intensity,
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


def seed():
    """
    @return: three :obj:`PROJECT` subjects for each collection in
        :obj:`COLLECTIONS`
    """
    # Initialize the pseudo-random generator.
    random.seed()
    # Make the subjects.
    coll_sbjs = ((_seed_collection(coll) for coll in COLLECTIONS))
    
    return chain.from_iterable(coll_sbjs)


def _seed_collection(collection):  
    return [_seed_subject(collection, sbj_nbr)
            for sbj_nbr in range(1, 4)]


def _seed_subject(collection, subject_number):  
    """
    Creates the subject if necessary.
    
    @return: the subject with the given collection and number
    """ 
    # If the subject is in the database, then delete it.
    try:
        sbj = Subject.objects.get(number=subject_number, project=PROJECT,
                                  collection=collection)
        print ("Del %s" % sbj.number)
    except Subject.DoesNotExist:
        pass    
    
    return _create_subject(collection, subject_number)


def _create_subject(collection, subject_number):
    sbj_dtl = _create_subject_detail(subject_number)
    sbj_dtl.save()
    sbj = Subject(number=subject_number, project=PROJECT,
                  collection=collection, detail=sbj_dtl)
    sbj.save()
    
    return sbj


def _create_subject_detail(subject_number):
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
    sessions = [_create_session(subject_number, sess_nbr) for sess_nbr in range(1, 5)]
    
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


def _create_session(subject_number, session_number):
    # Bump the session month.
    mo = subject_number * session_number
    # Stagger the inter-session duration.
    day = DATE_0.day + ((session_number - 1) * 5)
    date = DATE_0.replace(month=mo, day=day)
    
    # The bolus arrival.
    arv = int(random.random() * 4) + 2
    
    # Add modeling parameters with a random offset.
    factor = 1 + ((random.random() - 0.5) * 0.4)
    fxl_k_trans = FXL_K_TRANS_AVG * factor
    factor = DELTA_K_TRANS_FACTOR + ((random.random() - 0.5) * 0.4)
    fxr_k_trans = fxl_k_trans * factor
    offset = (0.5 - random.random()) * 0.2
    v_e = V_E_0 + offset
    offset = (0.5 - random.random()) * 0.2
    tau_i = TAU_I_0 + offset
    name = "pk_%d" % (((subject_number - 1) * 3) + session_number)
    modeling = Modeling(name=name, fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                        v_e=v_e, tau_i=tau_i)
    
    # Make the intensity probe.
    probe = Probe(description='ROI centroid', location=[13.0, 85.4, 14.1])

    # Make the scan.
    scan = _create_scan(probe)
    
    # Make the registration.
    registration = _create_registration(probe, session_number)

    # Make the session detail.
    sess_dtl = SessionDetail(bolus_arrival_index=arv, scan=scan,
                             reconstructions=[registration])
    
    # Save the detail.
    sess_dtl.save()
    
    return Session(number=session_number, acquisition_date=date,
                   modeling=modeling, detail=sess_dtl)


def _create_scan(probe):
    files = ["series%02d.nii.gz" % i for i in range(1,33)]
    intensity = _create_intensity(probe)
    # Add a motion artifact.
    start = 12 + int(random.random() * 5)
    for i in range(start, start + 5):
        intensity.intensities[i] -= random.random() * 8
    
    return Scan(files=files, intensity=intensity)


def _create_registration(probe, session_number):
    
    name = "reg_%02d" % session_number
    files = ["%s_series%02d.nii.gz" % (name, i) for i in range(1,33)]
    intensity = _create_intensity(probe)

    return Reconstruction(name=name, files=files, intensity=intensity)
    

def _create_intensity(probe):
    # Ramp intensity up logarithmically until bolus arrival.
    intensities = [(math.log(i) * 20) + (random.random() * 5) for i in range(1, 7)]
    arv_intensity = intensities[5]
    # Tail intensity off inverse exponentially thereafter.
    for i in range(1, 27):
        intensity = (math.exp(-2 * (float(i)/25)) * arv_intensity) + (random.random() * 5)
        intensities.append(intensity)

    return Intensity(probe=probe, intensities=intensities)

if __name__ == "__main__":
    seed()
