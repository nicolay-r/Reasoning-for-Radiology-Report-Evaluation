from mmi_kit.service_os import OsService


class ServiceBase(object):
    pass


class TCGA_LIHC_Service(ServiceBase):

    @staticmethod
    def metadata_search(dir_path, template="metadata.csv"):
        data_it = OsService.iter_dir_filepaths(
            dir_path, filter_full_path=lambda filepath: template in filepath)
        filepath = next(data_it)
        return filepath


class CPTAC_CCRCC_Service(TCGA_LIHC_Service):
    """ This iterator aimed at grouped iteration of the
        patients-related series iterations.
    """
    pass