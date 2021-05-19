import pandas as pd
import numpy as np
from src.data_cleaning import data_cleaner


ALLOWED_EXTENSIONS = set(['sm', 'ssc'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_feature_values(data, verifier):
    """ Given a params dict, return the values for feeding into a model"""  
    #confirms that the user selected "tech"
    if verifier==str(0):
        stamina=False
        feature_values=data_cleaner(data, is_stamina=False)
        feature_values['stream_log_transform']=np.where(feature_values['stream_total'] > 0, np.log(feature_values['stream_total']), feature_values['stream_total'])
        return feature_values, stamina
    #else, the user selected stamina    
    else:
        stamina=True
        feature_values=data_cleaner(data, is_stamina=True)
        feature_values['stream_log_transform']=np.where(feature_values['stream_total'] > 0, np.log(feature_values['stream_total']), feature_values['stream_total'])
        return feature_values, stamina

