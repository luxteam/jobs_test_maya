import os.path as path
from shutil import copyfile
import sys
import traceback
sys.path.append(path.abspath(path.join(path.dirname(__file__), path.pardir, path.pardir, path.pardir)))
from jobs_launcher.core.config import main_logger


def process_results(output):
    try:
        with open(path.join(output, 'renderTool.log')) as f:
            if 'successfully uploaded data to AWS!' in f.read():
                main_logger.info("Replace rendered image by passed image (Athena extension)")
                copyfile(path.join(output, '..', '..', '..', '..', 'jobs_launcher', 'common',
                                   'img', 'passed.jpg'), path.join(output, 'Color', 'MAYA_RS_AWS_001.jpg'))
            else:
                main_logger.info("Replace rendered image by error image (Athena extension)")
                copyfile(path.join(output, '..', '..', '..', '..', 'jobs_launcher', 'common',
                                   'img', 'error.jpg'), path.join(output, 'Color', 'MAYA_RS_AWS_001.jpg'))
    except Exception as e:
        main_logger.error("Failed to execute Athena extension. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))
