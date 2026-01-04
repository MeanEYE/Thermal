import textwrap

from ..base.component import Component


class Text(Component):
	"""Simple text component which supports text wrapping and
	clipping. Component can be used to keep variable text as well
	as used like title. Content is always parsed before being
	printed."""

	def __init__(self, text):
		self.value = text
		self.code_page = None

	def set_code_page(self, code_page):
		"""Set encoding for this bit of text."""
		self.code_page = code_page

	def set_text(self, value):
		"""Set value of the text container."""
		self.value = value

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		text = textwrap.wrap(
				self.printer.parse(self.value),
				width=width,
				expand_tabs=True,
				replace_whitespace=True,
				fix_sentence_endings=False,
				break_long_words=True,
				drop_whitespace=True,
				break_on_hyphens=True,
				tabsize=4,
				max_lines=None,
				placeholder='…'
				)

		# apply code pages if needed
		if self.code_page is not None:
			text[0] = self.printer.set_code_page(self.code_page) + text[0]
			text[-1] = text[-1] + self.printer.set_code_page(self.printer.default_code_page)

		return text
