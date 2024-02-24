import argparse
import download.download_module as ad

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--schedule", action="store_true", help="download schedule, busstop and lines")
parser.add_argument("number_of_times", help="number of files with current coordinates to download")
args = parser.parse_args()


if args.schedule:
    ad.download_data(args.number_of_times, True, True)
else:
    ad.download_data(args.number_of_times, False, True)
