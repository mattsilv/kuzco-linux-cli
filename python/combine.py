import os
import argparse

def combine_files(directory, output_file, extensions):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    outfile.write(f"File: {file_path}\n")
                    outfile.write("=" * 50 + "\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file: {str(e)}\n")
                    outfile.write("\n" + "=" * 50 + "\n\n")

def main():
    parser = argparse.ArgumentParser(description="Combine file contents from a directory.")
    parser.add_argument("-d", "--directory", default=".", 
                        help="Directory to search for files (default: current directory)")
    parser.add_argument("output", help="Output file name")
    parser.add_argument("--extensions", nargs="+", default=[".py", ".txt"], 
                        help="File extensions to include (default: .py .txt)")

    args = parser.parse_args()

    # Use os.path.abspath to get the full path of the directory
    directory = os.path.abspath(args.directory)
    print(f"Searching in directory: {directory}")

    combine_files(directory, args.output, args.extensions)
    print(f"Combined file contents written to {args.output}")

if __name__ == "__main__":
    main()