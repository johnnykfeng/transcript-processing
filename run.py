
from transcript_processing_functions import \
                        full_transcript2essay, \
                        extract_metadata_as_json, \
                        json2rst
import os
import json

if __name__ == '__main__':
    essay_filepath = r'./essays/test_essay.txt'
    if not os.path.exists(essay_filepath): # if essay doesn't exist
        print('Generating essay... (this may take a few minutes)')

        transcript_filepath = r'./transcripts/test_transcript.md'
        with open(transcript_filepath, 'r') as file:
            raw_transcript = file.read()

        # takes about 2-3 minutes to run
        final_essay = full_transcript2essay(raw_transcript)

        essay_filepath = r'./essays/test_essay.txt'
        # save the final essay to a file
        with open(essay_filepath, 'w') as file:
            file.write(final_essay)

    # start here if essay exists

    # load essay from file
    essay_filepath = r'./essays/test_essay.txt'
    with open(essay_filepath, 'r') as file:
        essay = file.read()

    # 17 seconds to run
    print('Extracting metadata...')
    metadata = extract_metadata_as_json(essay)

    # save metadata to file
    metadata_filepath = r'./metadata/test_metadata.json'
    with open(metadata_filepath, 'w') as file:
        json.dump(metadata, file)

    # convert metadata from json to rst
    rst_filepath = r'./metadata/test.rst'
    json2rst(metadata, rst_filepath)


