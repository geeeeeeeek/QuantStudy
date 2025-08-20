import pandas as pd

from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

# zipline bundles
# cp extension.py ~/.zipline/
# zipline ingest -b custom-csv-bundle

start_session = pd.Timestamp('2012-1-3', tz='utc')
end_session = pd.Timestamp('2014-12-31', tz='utc')

register(
    'custom-csv-bundle',
    csvdir_equities(
        ['daily'],
        '/Users/xiaoqingsong/py_study/zipline_demo/csvdir'
    ),
    calendar_name='XNYS',  # US equities
    start_session=start_session,
    end_session=end_session
)
