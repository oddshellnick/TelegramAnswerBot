class LocalizationError(Exception):
	def __init__(self, language: str, localization_item: str):
		super().__init__(f"{localization_item} has no localization in {language.upper()}")
