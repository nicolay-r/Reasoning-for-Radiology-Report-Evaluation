class SpreadsheetService(object):

    @staticmethod
    def format_line(args_list):
        return "\t".join([str(v) for v in args_list])
