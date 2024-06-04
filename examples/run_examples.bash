#!/bin/bash

# Define directories
INPUT_DIR="example_content"
OUTPUT_DIR="expected_outputs"
EXAMPLES_DIR="."

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Iterate over all .sbignore* files
for ignore_file in $EXAMPLES_DIR/.sbignore*; do
    # Check if there are no matching files
    if [ ! -e "$ignore_file" ]; then
        echo "No .sbignore files found in $IGNORE_FILES_DIR"
        exit 1
    fi

    # Extract the base name of the ignore file
    ignore_filename=$(basename "$ignore_file")
    
    # Generate the output CSV filename
    output_filename="${ignore_filename#.sbignore_}.csv"
    output_filename="ignore_$output_filename"
    output_filepath="$OUTPUT_DIR/$output_filename"
    
    # Run the sum-buddy command
    sum-buddy --output-file "$output_filepath" --ignore-file "$ignore_file" --algorithm md5 "$INPUT_DIR"
    
    echo "Wrote $output_filepath using $ignore_file"
done

# Run sum-buddy for the default case (neither --ignore-file nor --include-hidden is passed)
default_output_filepath="$OUTPUT_DIR/default.csv"
sum-buddy --output-file "$default_output_filepath" --algorithm md5 "$INPUT_DIR"
echo "Wrote $default_output_filepath with default settings"

# Run sum-buddy for the case where --include-hidden is True
include_hidden_true_output_filepath="$OUTPUT_DIR/include_hidden_true.csv"
sum-buddy --output-file "$include_hidden_true_output_filepath" --include-hidden --algorithm md5 "$INPUT_DIR"
echo "Wrote $include_hidden_true_output_filepath with --include-hidden True"
