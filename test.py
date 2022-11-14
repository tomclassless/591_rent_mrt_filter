import pandas as pd

seen_df = pd.read_csv('591/list/seen.csv')

seen_df['exist'] = True

seen_df.loc[seen_df['post_id'].isin([13460861]), 'exist'] = False

seen_df.to_csv('591/list/seen.csv', index=False)
