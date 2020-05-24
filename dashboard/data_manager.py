import s3fs
# import fastparquet as fp
import pandas as pd
s3 = s3fs.S3FileSystem()
fs = s3fs.core.S3FileSystem()

DATA_BUCKET_NAME = 'ollascomuneschile'
DATA_BUCKET_REGION = 'ollascomuneschile'

PROCESSED_DATA_PREFIX_KEY = ''


def get_ollascomunes_df():
    return pd.read_csv('EmiliaRiosS_01-03-2020.csv')

    data_s3_path = f'{DATA_BUCKET_NAME}/algunacarpeta/*/*.parquet'
    all_paths_from_s3 = fs.glob(path=data_s3_path)

    fp_obj = fp.ParquetFile(all_paths_from_s3, open_with=s3.open, root=data_s3_path)
    df = fp_obj.to_pandas()
    return df

def get_columnas_df():
    pass
