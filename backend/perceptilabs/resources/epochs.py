import re
import os
import pickle

from perceptilabs.utils import b64decode_and_sanitize

class EpochsAccess:
    def get_latest(self, training_session_id, require_checkpoint=True, require_trainer_state=False):
        if training_session_id is None:
            return None

        epochs = self._get_epochs(training_session_id)
        current_id = None
        current_modification = -1
        for epoch_id in epochs.keys():
            checkpoint_modified = epochs[epoch_id].get('checkpoint_modified')
            state_modified = epochs[epoch_id].get('state_modified')

            if checkpoint_modified is None and require_checkpoint:
                continue
            if state_modified is None and require_trainer_state:
                continue

            latest_modification = max(checkpoint_modified or -1, state_modified or -1)

            if latest_modification > current_modification:
                current_id = epoch_id                
                current_modification = latest_modification

        return current_id

    def has_saved_epoch(self, training_session_id, require_checkpoint=True, require_trainer_state=True):
        epoch_id = self.get_latest(
            training_session_id=training_session_id, 
            require_checkpoint=require_checkpoint,
            require_trainer_state=require_trainer_state
        )
        return epoch_id is not None        

    def get_checkpoint_path(self, training_session_id, epoch_id):
        if training_session_id is None or epoch_id is None:
            return None
        
        directory = self._resolve_directory_path(training_session_id)
        file_path = os.path.join(directory, 'checkpoint-{epoch_id:04d}.ckpt'.format(
            epoch_id=int(epoch_id)))
        return file_path

    def _get_state_path(self, training_session_id, epoch_id):
        directory = self._resolve_directory_path(training_session_id)
        file_path = os.path.join(directory, 'state-{epoch_id:04d}.pkl'.format(
            epoch_id=int(epoch_id)))
        return file_path    

    def load_state_dict(self, training_session_id, epoch_id):
        if training_session_id is None or epoch_id is None:
            return None
        
        path = self._get_state_path(training_session_id, epoch_id)        
        
        with open(path, 'rb') as f:
            state_dict = pickle.load(f)
            return state_dict

    def save_state_dict(self, training_session_id, epoch_id, state_dict):
        if training_session_id is None or epoch_id is None or state_dict is None:
            return None
        
        path = self._get_state_path(training_session_id, epoch_id)
        
        with open(path, 'wb') as f:
            pickle.dump(state_dict, f)

    def _resolve_directory_path(self, training_session_id):
        directory = b64decode_and_sanitize(training_session_id)  # For now it's just a base64 path
        return directory

    def _get_epochs(self, training_session_id):
        directory = self._resolve_directory_path(training_session_id)
        if not os.path.isdir(directory):
            return {}        
        
        self._resolve_checkpoint_filenames(directory)
        
        def resolve_epoch_and_type(file_name):
            match = re.fullmatch('checkpoint-([0-9]*).ckpt.index', file_name)
            if match:
                return int(match.group(1)), 'checkpoint'

            match = re.fullmatch('state-([0-9]*).pkl', file_name)
            if match:
                return int(match.group(1)), 'state'

            return None, None
        
        epochs = {}
        for file_name in os.listdir(directory):
            epoch_id, file_type = resolve_epoch_and_type(file_name)
            if epoch_id is not None:
                if epoch_id not in epochs:
                    epochs[epoch_id] = {'checkpoint_modified': None, 'state_modified': None}

                file_path = os.path.join(directory, file_name)
                epochs[epoch_id][file_type + '_modified'] = os.path.getmtime(file_path)
        return epochs
    
    
    def _resolve_checkpoint_filenames(self, directory):
            for file in os.listdir(directory):
                if 'checkpoint.ckpt' in file:
                    try:
                        src = os.path.join(directory, file)
                        dst = os.path.join(directory, file.replace('checkpoint.ckpt', 'checkpoint-0000.ckpt'))
                        os.rename(src, dst)
                    except:
                        pass
                if 'state.pkl' in file:
                    try:
                        src = os.path.join(directory, file)
                        dst = os.path.join(directory, file.replace('state.pkl', 'state-0000.pkl'))
                        os.rename(src, dst)
                    except:
                        pass
            return

        

