import datman.scanid as scanid
import pytest

SETTINGS = {
    'ID_TYPE': 'KCNI',
    'STUDY': 'DTI',
    'SITE': {
        'CMH': 'UT1',
        'UTO': 'UT2'
    },
    'SUBJECT': {
        '9(?P[0-9]{3,8})': 'H',
        '8(?P[0-9]{3,8})': 'C'
    }
}


def test_parse_empty():
    with pytest.raises(scanid.ParseException):
        scanid.parse("")


def test_parse_None():
    with pytest.raises(scanid.ParseException):
        scanid.parse(None)


def test_parse_garbage():
    with pytest.raises(scanid.ParseException):
        scanid.parse("lkjlksjdf")


def test_parse_good_datman_scanid():
    ident = scanid.parse("DTI_CMH_H001_01_02")
    assert ident.study == "DTI"
    assert ident.site == "CMH"
    assert ident.subject == "H001"
    assert ident.timepoint == "01"
    assert ident.session == "02"


def test_parse_good_datman_PHA_scanid():
    ident = scanid.parse("DTI_CMH_PHA_ADN0001")
    assert ident.study == "DTI"
    assert ident.site == "CMH"
    assert ident.subject == "PHA_ADN0001"
    assert ident.timepoint == ""
    assert ident.session == ""
    assert str(ident) == "DTI_CMH_PHA_ADN0001"


def test_parse_good_kcni_scanid():
    ident = scanid.parse("ABC01_CMH_12345678_01_SE02_MR")
    assert ident.study == 'ABC01'
    assert ident.site == 'CMH'
    assert ident.subject == '12345678'
    assert ident.timepoint == '01'
    assert ident.session == '02'


def test_parse_good_kcni_PHA_scanid():
    ident = scanid.parse("ABC01_CMH_LEGPHA_0001_MR")
    assert ident.study == 'ABC01'
    assert ident.site == 'CMH'
    assert ident.subject == 'PHA_LEG0001'


# def test_parse_and_modify_kcni_scanid_when_given_settings():
#     ident = scanid.parse('DTI01_UTO_9001_01_SE02_MR', settings=SETTINGS)
#     assert ident.study == 'DTI'
#     assert ident.site == 'UT2'
#     assert ident.subject == 'H001'
#     assert ident.timepoint == '01'
#     assert ident.session == '02'

def test_parses_datman_subject_id_as_datman_identifier():
    dm_subject = "DTI01_CMH_H001_01_02"
    ident = scanid.parse(dm_subject)
    assert isinstance(ident, scanid.DatmanIdentifier)


def test_parses_datman_pha_id_as_datman_identifier():
    dm_pha = "DTI01_CMH_PHA_H001"
    ident = scanid.parse(dm_pha)
    assert isinstance(ident, scanid.DatmanIdentifier)


def test_parses_kcni_subject_id_as_kcni_identifier():
    kcni_subject = "DTI01_CMH_H001_01_SE02_MR"
    ident = scanid.parse(kcni_subject)
    assert isinstance(ident, scanid.KCNIIdentifier)


def test_parses_kcni_pha_id_as_kcni_identifier():
    kcni_pha = "DTI01_CMH_ABCPHA_0001_MR"
    ident = scanid.parse(kcni_pha)
    assert isinstance(ident, scanid.KCNIIdentifier)


def test_is_scanid_garbage():
    assert not scanid.is_scanid("garbage")


def test_is_scanid_subjectid_only():
    assert not scanid.is_scanid("DTI_CMH_H001")


def test_is_scanid_extra_fields():
    assert scanid.is_scanid("DTI_CMH_H001_01_01_01_01_01_01") is False


def test_is_datman_scanid_good():
    assert scanid.is_scanid("SPN01_CMH_0002_01_01")


def test_is_kcni_scanid_good():
    assert scanid.is_scanid("SPN01_CMH_0001_01_SE01_MR")


def test_get_full_subjectid():
    ident = scanid.parse("DTI_CMH_H001_01_02")
    assert ident.get_full_subjectid() == "DTI_CMH_H001"


def test_subject_id_with_timepoint():
    ident = scanid.parse("DTI_CMH_H001_01_02")
    assert ident.get_full_subjectid_with_timepoint() == 'DTI_CMH_H001_01'


def test_PHA_timepoint():
    ident = scanid.parse("DTI_CMH_PHA_ADN0001")
    assert ident.get_full_subjectid_with_timepoint() == 'DTI_CMH_PHA_ADN0001'


def test_parse_filename():
    ident, tag, series, description = scanid.parse_filename(
        'DTI_CMH_H001_01_01_T1_03_description.nii.gz')
    assert str(ident) == 'DTI_CMH_H001_01_01'
    assert tag == 'T1'
    assert series == '03'
    assert description == 'description'


def test_parse_filename_PHA():
    ident, tag, series, description = scanid.parse_filename(
        'DTI_CMH_PHA_ADN0001_T1_02_description.nii.gz')
    assert str(ident) == 'DTI_CMH_PHA_ADN0001'
    assert tag == 'T1'
    assert series == '02'
    assert description == 'description'


def test_parse_filename_PHA_2():
    ident, tag, series, description = scanid.parse_filename(
        'SPN01_MRC_PHA_FBN0013_RST_04_EPI-3x3x4xTR2.nii.gz')
    assert ident.study == 'SPN01'
    assert ident.site == 'MRC'
    assert ident.subject == 'PHA_FBN0013'
    assert ident.timepoint == ''
    assert ident.session == ''
    assert str(ident) == 'SPN01_MRC_PHA_FBN0013'
    assert tag == 'RST'
    assert series == '04'
    assert description == 'EPI-3x3x4xTR2'


def test_parse_filename_with_path():
    ident, tag, series, description = scanid.parse_filename(
        '/data/DTI_CMH_H001_01_01_T1_02_description.nii.gz')
    assert str(ident) == 'DTI_CMH_H001_01_01'
    assert tag == 'T1'
    assert series == '02'
    assert description == 'description'


def test_parse_bids_filename():
    ident = scanid.parse_bids_filename("sub-CMH0001_ses-01_run-1_T1w.nii.gz")
    assert ident.subject == 'CMH0001'
    assert ident.session == '01'
    assert ident.run == '1'
    assert ident.suffix == 'T1w'


def test_parse_bids_filename_with_full_path():
    ident = scanid.parse_bids_filename(
        "/some/folder/sub-CMH0001_ses-01_run-1_T1w.nii.gz")
    assert ident.subject == 'CMH0001'
    assert ident.session == '01'
    assert ident.run == '1'
    assert ident.suffix == 'T1w'


def test_parse_bids_filename_without_ext():
    ident = scanid.parse_bids_filename(
        "/some/folder/sub-CMH0001_ses-02_run-3_T1w")
    assert ident.subject == 'CMH0001'
    assert ident.session == '02'
    assert ident.run == '3'
    assert ident.suffix == 'T1w'


def test_parse_bids_filename_without_run():
    scanid.parse_bids_filename("sub-CMH0001_ses-01_T1w.nii.gz")


def test_parse_bids_filename_missing_subject():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("ses-01_run-1_T1w")


def test_parse_bids_filename_malformed_subject():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("CMH0001_ses-01_run-1_T1w")


def test_parse_bids_filename_missing_session():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_run-1_T1w")


def test_parse_bids_filename_malformed_session():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_ses-_run-1_T1w")


def test_parse_bids_filename_missing_suffix():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_ses-01_run-1.nii.gz")


def test_parse_bids_filename_missing_suffix_and_run():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_ses-01.nii.gz")


def test_unknown_entity_does_not_get_set_as_suffix():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH_ses-01_new-FIELD_T1w.nii.gz")


def test_empty_entity_name_does_not_get_set_as_suffix():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH_ses-01_-FIELD_T1w.nii.gz")


def test_empty_entity_name_and_label_does_not_get_set_as_suffix():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH_ses-01_-_T1w.nii.gz")


def test_bids_file_raises_exception_when_wrong_entities_used_for_anat():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename(
            "sub-CMH0001_ses-01_ce-somefield_dir-somedir"
            "_run-1_T1w.nii.gz")


def test_bids_file_raises_exception_when_wrong_entities_used_for_task():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_ses-01_task-sometask_"
                                   "ce-somefield_run-1_T1w.nii.gz")


def test_bids_file_raises_exception_when_wrong_entities_used_for_fmap():
    with pytest.raises(scanid.ParseException):
        scanid.parse_bids_filename("sub-CMH0001_ses-01_dir-somedir_"
                                   "rec-somefield_run-1_T1w.nii.gz")


def test_optional_entities_dont_get_parsed_as_suffix():
    optional_entities = "sub-CMH0001_ses-01_{}_T1w.nii.gz"
    for entity in ['run', 'acq', 'ce', 'rec', 'echo', 'ce', 'mod', 'task']:
        optional_field = '{}-11'.format(entity)
        bids_name = optional_entities.format(optional_field)
        parsed = scanid.parse_bids_filename(bids_name)
        assert optional_field not in parsed.suffix


def test_bids_file_equals_string_of_itself():
    bids_name = "sub-CMH0001_ses-01_run-1_T1w"
    ident = scanid.parse_bids_filename(bids_name)
    assert ident == bids_name


def test_bids_file_equals_string_of_itself_minus_run():
    bids_name = "sub-CMH0001_ses-01_run-1_T1w"
    ident = scanid.parse_bids_filename(bids_name)
    assert ident == bids_name.replace("run-1_", "")


def test_bids_file_equals_itself_with_path_and_ext():
    bids_name = "sub-CMH0001_ses-01_run-1_T1w"
    bids_full_path = "/some/folder/somewhere/{}.nii.gz".format(bids_name)
    ident = scanid.parse_bids_filename(bids_name)
    assert ident == bids_full_path


def test_bids_file_correctly_parses_when_all_anat_entities_given():
    anat_bids = "sub-CMH0001_ses-01_acq-abcd_ce-efgh_rec-ijkl_" + \
                "run-1_mod-mnop_somesuffix"

    parsed = scanid.parse_bids_filename(anat_bids)
    assert str(parsed) == anat_bids


def test_bids_file_correctly_parses_when_all_task_entities_given():
    task_bids = "sub-CMH0001_ses-01_task-abcd_acq-efgh_" + \
                "rec-ijkl_run-1_echo-11_imi"

    parsed = scanid.parse_bids_filename(task_bids)
    assert str(parsed) == task_bids


def test_bids_file_correctly_parses_when_all_fmap_entities_given():
    fmap_bids = "sub-CMH0001_ses-01_acq-abcd_dir-efgh_run-1_fmap"

    parsed = scanid.parse_bids_filename(fmap_bids)
    assert str(parsed) == fmap_bids


def test_bids_file_handles_prelapse_session_strings():
    prelapse_file = "sub-BRG33006_ses-01R_run-1_something"

    parsed = scanid.parse_bids_filename(prelapse_file)
    assert str(parsed) == prelapse_file
