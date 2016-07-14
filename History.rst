This history lists major release themes. See the GitHub commits
for change details.

6.2.1 / 2016-07-14
------------------
* Add Project.

6.1.1 / 2016-07-06
------------------
* Rename from qiprofile-rest to qirest.

5.8.1 / 2016-07-06
------------------
* Add --clinical and --project seed options.

5.7.5 / 2016-04-26
------------------
* Set the seed bolus arrival index.

5.7.4 / 2016-03-22
------------------
* Upgrade the Eve and pymongo versions.

5.7.3 / 2016-03-18
------------------
* Pick up REST data model Resource changes.

5.7.2 / 2016-03-03
------------------
* Test reseed by subject string comparison.

5.7.1 / 2016-02-24
------------------
* Add the ImagingCollection model.

5.6.7 / 2016-02-22
------------------
* Add the ImagingCollection.

5.6.6 / 2016-02-03
------------------
* Bump the client version.

5.6.5 / 2016-02-03
------------------
* Add colorizations.

5.6.4 / 2015-12-23
-----------------
* Adapt seed to the REST data model v5.9.1 imaging changes.

5.6.3 / 2015-11-04
------------------
* Adapt seed to the REST data model ModelingProtocol parameters change.

5.6.2 / 2015-10-26 
------------------
* Correct the environment option help text.

5.6.1 / 2015-09-15
------------------
* Make the default environment development rather than production.

5.5.1 / 2015-09-15
------------------
* Get the seed connection parameters from the Eve settings.

5.4.5 / 2015-09-09
------------------
* Qualify tumor location.

5.4.4 / 2015-08-10
------------------
* Add Heroku settings and Mongo env var overrides.

5.4.3 / 2015-08-02
------------------
* Bump REST client version.

5.4.2 / 2015-08-02
------------------
* Add RCB to the seed utility.

5.4.1 / 2015-07-28
------------------
* Add tumors to the seed utility.

5.3.1 / 2015-06-25
------------------
* Upgrade to Mongo 3.

5.2.4 / 2015-06-23
------------------
* Use BreastSurgery in the seed utility.

5.2.3 / 2015-06-18
------------------
* No, dosage amount is now a float.
* Sarcoma grade necrosis was renamed to necrosis_score.

5.2.2 / 2015-06-15
------------------
* Dosage amount is an integer.

5.2.1 / 2015-06-09
------------------
* Session is an encounter.

5.1.9 / 2015-06-03
------------------
* The REST client BreastPathology receptor_status is a list.

5.1.8 / 2015-05-26
------------------
* The REST client SarcomaPathology necrosis_pct field is renamed
  to necrosis_percent.

5.1.7 / 2015-05-15
------------------
* Adapt for the REST client package changes.

5.1.6 / 2015-05-05
------------------
* Redeploy.

5.1.5 / 2015-05-05
------------------
* Update qiutil version.

5.1.4 / 2015-04-08
------------------
* Add the seed subject weights.

5.1.4 / 2015-04-07
------------------
* Move subject weight from Subject to Session.

5.1.3 / 2015-04-03
------------------
* Bump client version.

5.1.2 / 2015-04-03
------------------
* Test genomic assay.

5.1.1 / 2015-02-20
------------------
* Split out qiprofile-rest-client.

4.1.2 / 2015-02-12
------------------
* Spawn python on the run.py script.

4.1.1 / 2015-02-12
------------------
* Add Volume into image hierarchy.

3.2.2 / 2015-02-06
------------------
* Distinguish the ScanSet scan_type and description.

3.2.1 / 2015-02-06
------------------
* Add API documentation.

3.1.2 / 2015-02-06
------------------
* Refactor models into separate modules.

3.1.1 / 2015-01-29
------------------
* Pull SubjectDetail into Subject.

2.4.1 / 2015-01-27
------------------
* Add gene expression assay.

2.3.3 / 2015-01-16
------------------
* Move registration configuration under scan set.

2.3.2 / 2014-12-17
------------------
* Adapt for PyPI.

2.3.1 / 2014-12-02
------------------
* Move modeling to registration configuration and scan set.

2.2.2 / 2014-11-04
------------------
* Add drug course.

2.2.1 / 2014-11-03
------------------
* Add T2 scans.

2.1.11 / 2014-10-02
------------------
* Add label_map.

2.1.10 / 2014-10-02
------------------
* Pipe server output to the console.

2.1.9 / 2014-09-09
------------------
* Embed the ModelingParameters.

2.1.8 / 2014-09-08
------------------
* More realistic seed race/ethnicity and timeline.

2.1.7 / 2014-09-05
------------------
* Format the test seed image file names per the XNAT convention.

2.1.6 / 2014-08-29
------------------
* Specialize the Sarcoma TNM score choices.

2.1.5 / 2014-08-28
------------------
* Accurately reflect the XNAT volume numbers and file names.

2.1.4 / 2014-08-18
------------------
* Encounter outcomes are optional.

2.1.4 / 2014-08-18
------------------
* Encounter outcomes are optional.

2.1.3 / 2014-08-11
------------------
* Break out TNM size scores in the data model.

2.1.2 / 2014-08-11
------------------
* Add treatments to the data model.

2.1.1 / 2014-07-17
------------------
* Replace the Django REST Mongo framework with Eve.

1.2.1 / 2014-05-22
------------------
* Registration is a XNAT resource rather than reconstruction.

1.1.1 / 2014-04-25
------------------
* Initial public release.
