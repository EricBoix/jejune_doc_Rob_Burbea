import os
import subprocess
import sys
import shutil
import argparse
from pdf_to_markdown import (
    MarkdownToDocument,
    PrintDocument,
)

DEBUG = False


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Convert Rob Burbea's document to canonical markdown."
    )
    parser.add_argument(
        "--output_directory",
        type=str,
        metavar="DIR",
        help="Relative path to output directory (default is CWD).",
    )
    parser.add_argument(
        "--maximum_line_length",
        type=int,
        metavar="N",
        default=None,
        help="Break paragraph lines longer than N characters (no new paragraph "
        "is introduced). 0 disables breaking (default: the converter's own value).",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help="Run pytest tests instead of converting.",
    )

    args = parser.parse_args()

    return args


class Converter:

    @staticmethod
    def markdown_output_filename():
        return "output.md"

    @staticmethod
    def markdown_output_filepath():
        return os.path.join(os.getcwd(), Converter.markdown_output_filename())

    def markdown_target_filename(self):
        file_no_ext = os.path.splitext(
            os.path.basename(self.original_document_filename)
        )[0]
        return file_no_ext + "_-_local_converter.md"

    # Lines of paragraphs longer than this are broken (markdownlint MD013),
    # without starting new paragraphs.
    DEFAULT_MAXIMUM_LINE_LENGTH = 800

    def __init__(self, original_document_filename, maximum_line_length=None):
        self.original_document_filename = original_document_filename
        if maximum_line_length is None:
            maximum_line_length = self.DEFAULT_MAXIMUM_LINE_LENGTH
        self.maximum_line_length = maximum_line_length

    def run(self):
        document_filename = os.path.join(
            os.path.dirname(__file__),
            "..",
            "original_data",
            self.original_document_filename,
        )

        document = MarkdownToDocument(document_filename).get_document()
        document.maximum_line_length = self.maximum_line_length
        # On debugging purposes
        if False:
            PrintDocument(document).pages()
            PrintDocument(document).paragraphs()
            PrintDocument(document).sentences()

        # Write the markdown file
        document.to_markdown(Converter.markdown_output_filepath())

    def move_outputs_to_output_dir(self, target_output_dir):
        converted_markdown_source = Converter.markdown_output_filepath()

        if not os.path.exists(converted_markdown_source):
            print(
                f"Converted markdown output file ({converted_markdown_source}) not found. Exiting."
            )
            sys.exit()

        converted_markdown_target = os.path.join(
            target_output_dir, self.markdown_target_filename()
        )
        shutil.move(converted_markdown_source, converted_markdown_target)
        if DEBUG:
            print("Following file moved to output:")
            print(f"  - {converted_markdown_target}")


def convert(original_document_filename, maximum_line_length=None):
    converter = Converter(original_document_filename, maximum_line_length)
    converter.run()
    return converter


if __name__ == "__main__":
    args = parse_arguments()
    if args.test:
        result = subprocess.run(["pytest", "test_main.py"])
        sys.exit(result.returncode)
    converter = convert(
        "2010_01_20_-_Rob_Burbea_-_Meditation_on_emptiness_Retreat_-_Opening_talk_Orienting_and_relating_to_the_emptiness_retreat.md",
        args.maximum_line_length,
    )
    if args.output_directory:
        converter.move_outputs_to_output_dir(args.output_directory)
