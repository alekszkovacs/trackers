import os
import re
import yaml


class CategoryMapper:
    """
    Maps vendors to categories.
    """

    def __init__(self):
        self.source_path = (
            f"{os.path.dirname(__file__)}/categories/vendor_category_mapper"
        )
        self._init_mapping(self.source_path)

    def _init_mapping(self, path: str) -> dict:
        self.mapping = {}
        list_dir = os.listdir(f"{os.path.abspath(path)}")
        for file_name in list_dir:
            if file_name.endswith(".yaml"):
                with open(f"{path}/{file_name}", "r") as f:
                    map = yaml.safe_load(f)
                    fn = file_name.split(".")[0]
                    self.mapping[fn] = map

    def map_from_vendor_list(self, vendors: list) -> list:
        try:
            result = []
            for vendor in vendors:
                _found = False
                for category, patterns in self.mapping.items():
                    if _found:
                        break
                    else:
                        for pattern in patterns:
                            if pattern and pattern.startswith("CS:"):
                                pattern = pattern.split("CS:")[1]
                                method = re.match(rf"{pattern}", vendor)
                            else:
                                method = re.match(rf"{pattern}", vendor, re.IGNORECASE)
                            if method:
                                _found = True
                                result.append(category)
                                break
                # if there was no break, then no match was found, so we have to add empty string
                if not _found:
                    result.append("")
            return result
        except Exception:
            # if you created a new yaml file, you should add a "-" to it, so it can be read as a list
            raise Exception(f"ADD LIST ELEMENT TO YAML FILE!")


### TESTS ###
# mapper = CategoryMapper()
# res = mapper.map_from_vendor_list(["ALBÁN PÉKiSÉG", "kuki", "Alza hu Budapest XIII", "MOL 12092 sz. toltoall", "MOL 61100 sz. toltoall", "MOL Limitless Mobility", "NYX*InnovatorKft", "OTPMOBL*VIMPAY.MAV-STA"])
# print(res)
