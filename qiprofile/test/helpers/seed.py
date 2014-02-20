import os
import datetime
import pytz
import random

# Set the settings environment variable before loading the models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')

from qiprofile.models import (Project, Collection, Subject, Session, Modeling)

DATE_0 = datetime.datetime(2013, 1, 4, tzinfo=pytz.utc)
"""The first acquisition date."""

DELTA_K_TRANS_0 = 0.1913
"""The first delta Ktrans value."""

TAU_I_0 = 0.4875
"""The first tau_i."""

V_E_0 = 0.6113
"""The first v_e vale."""


def seed():
    # Create the project, if necessary.
    try:
        prj = Project.objects.get(name='QIN_Test')
    except Project.DoesNotExist:
        prj = Project(name='QIN_Test')
        prj.save()
    
    # Create the subjects as needed.
    for coll in Collection.objects.all():
        for sbj_nbr in range(1, 4):
            try:
                sbj = Subject.objects.get(number=sbj_nbr, project=prj,
                                          collection=coll)
            except Subject.DoesNotExist:
                sbj = Subject(number=sbj_nbr, project=prj, collection=coll)
                sbj.save()
            
            # Make the sessions.
            for sess_nbr in range(1, 5):
                try:
                    sess = Session.objects.get(number=sess_nbr, subject=sbj)
                except Session.DoesNotExist:
                    sess = _create_session(sbj, sess_nbr)


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
    sess.save()
    
    return sess


if __name__ == "__main__":
    seed()
