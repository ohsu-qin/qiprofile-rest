import os
import datetime
import pytz
import random

# Set the settings environment variable before loading the models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')

from qiprofile_rest.models import (Subject, SubjectDetail, Session, Modeling)

PROJECT = 'QIN_Test'

COLLECTIONS = ['Breast', 'Sarcoma']

DATE_0 = datetime.datetime(2013, 1, 4, tzinfo=pytz.utc)
"""The first acquisition date."""

DELTA_K_TRANS_0 = 0.1913
"""The first delta Ktrans value."""

TAU_I_0 = 0.4875
"""The first tau_i."""

V_E_0 = 0.6113
"""The first v_e vale."""


def seed():    
    # Create the subjects as needed.
    for coll in COLLECTIONS:
        for sbj_nbr in range(1, 4):
            try:
                sbj = Subject.objects.get(number=sbj_nbr, project=PROJECT,
                                          collection=coll)
            except Subject.DoesNotExist:
                sbj = Subject(number=sbj_nbr, project=PROJECT, collection=coll)
                print sbj
                #sbj.save()
            
            # Make the subject detail.
            if not sbj.subject_detail:
                sbj_dtl = SubjectDetail()
            
            # Make the sessions.
            for sess_nbr in range(1, 5):
                try:
                    sess = Session.objects.get(number=sess_nbr)
                except Session.DoesNotExist:
                    sess = _create_session(sbj, sess_nbr)


def _create_subject_detail():
    # The patient demographics.
    yr = int(40 * random.random()) + 1950
    birth_date = datetime.datetime(yr, 7, 7, tzinfo=pytz.utc)
    race = choices.RACE_CHOICES[int(len(choices.RACE_CHOICES) * random.random())][0]
    
    # Make the encounters.
    biopsy = Encounter(encounter_type='Biopsy', )
    
    # Make the session.
    sess = Session(number=session_number, subject=subject,
                   acquisition_date=date)
    
    # Add modeling parameters with a random offset.
    offset = (0.5 - random.random()) * 0.2
    delta_k_trans = DELTA_K_TRANS_0 + offset
    offset = (0.5 - random.random()) * 0.2
    v_e = V_E_0 + offset
    offset = (0.5 - random.random()) * 0.2
    tau_i = TAU_I_0 + offset
    name = "pk_%d" % (((subject.number - 1) * 3) + session_number)
    sess.modeling = Modeling(name=name, session=sess,
                             delta_k_trans=delta_k_trans,
                             v_e=v_e, tau_i=tau_i)


def _create_session(subject, session_number):
    # Bump the session month.
    mo = session_number * subject.number
    # Stagger the inter-session duration.
    day = DATE_0.day + ((session_number - 1) * 5)
    date = DATE_0.replace(month=mo, day=day)
    
    # Make the session.
    sess = Session(number=session_number, subject=subject,
                   acquisition_date=date)
    
    # Add modeling parameters with a random offset.
    offset = (0.5 - random.random()) * 0.2
    delta_k_trans = DELTA_K_TRANS_0 + offset
    offset = (0.5 - random.random()) * 0.2
    v_e = V_E_0 + offset
    offset = (0.5 - random.random()) * 0.2
    tau_i = TAU_I_0 + offset
    name = "pk_%d" % (((subject.number - 1) * 3) + session_number)
    sess.modeling = Modeling(name=name, session=sess,
                             delta_k_trans=delta_k_trans,
                             v_e=v_e, tau_i=tau_i)
    
    # Save the new session.
    print sess
    #sess.save()
    
    return sess


if __name__ == "__main__":
    seed()
