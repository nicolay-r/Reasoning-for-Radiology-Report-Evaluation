class BaseOntology(object):

    UNKN_VALUE = "?"

    def __init__(self, ontology_dict):
        assert (isinstance(ontology_dict, dict))
        self.__ontology_dict = ontology_dict

    @property
    def Name(self):
        raise NotImplemented()

    def iter_ontology_parsers(self, parser_type):
        """ This is an ontology provider for the particular type of field parsers.
            The Concept is the actual ontology is not available since it shares different approaches on result handling.
        """
        assert (isinstance(parser_type, str) and parser_type in ["llm", "manual"])
        assert (isinstance(self.__ontology_dict, dict))

        for k, v in self.__ontology_dict.items():
            yield k, v[parser_type]

    def get_ontology_labels(self, key, keep_unknown=False):
        labels_ref = self.__ontology_dict[key].get("labels", None)

        # IMPORTANT: Make a copy of the list.
        labels = list(labels_ref) if labels_ref is not None else labels_ref

        if not keep_unknown and self.UNKN_VALUE in labels:
            labels.remove(self.UNKN_VALUE)

        return labels

    def iter_ontology_keys(self):
        return self.__ontology_dict.keys()

    def ontology_series_mapping(self):
        """ This is method for series mapping onto patient related data.
        """
        raise Exception("NOT IMPLEMENTED.")

    def ontology_mapping_header(self):
        """ This is method is for arranging list of columns to be considered.
        """
        raise Exception("NOT IMPLEMENTED.")

    def get_header(self):
        raise Exception("NOT IMPLEMENTED.")
