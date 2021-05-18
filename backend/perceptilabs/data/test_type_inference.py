import pytest
import pandas as pd


from perceptilabs.data.type_inference import TypeInferrer


@pytest.fixture
def df():
    data = {
        'Name': ['Tom', 'Joseph', 'Krish', 'John'],
        'City': ['Stockholm', 'Stockholm', 'Gothenburg', 'San Francisco'],        
        'Age': [20, 21, 19, 18],
        'Height': [177.3, 160.2, 165.2, 190.4],        
        'Gender': ['Male', 'Male', 'Female', 'Male'],
        'Photo': ['tom.jpg', 'joseph.jpg', 'krish.jpg', 'john.jpg']
    }  
    df = pd.DataFrame(data)  
    yield df


def test_identifies_text(df):
    inferrer = TypeInferrer()
    assert inferrer.is_valid_text(df['Name'])
    assert inferrer.is_valid_text(df['City'])
    assert inferrer.is_valid_text(df['Gender'])
    assert inferrer.is_valid_text(df['Photo'])                    
    assert not inferrer.is_valid_text(df['Age'])
    assert not inferrer.is_valid_text(df['Height'])    

    
def test_identifies_categorical(df):
    inferrer = TypeInferrer(max_categories=3)
    assert inferrer.is_valid_categorical(df['City'])
    assert inferrer.is_valid_categorical(df['Gender'])
    assert not inferrer.is_valid_categorical(df['Name'])
    assert not inferrer.is_valid_categorical(df['Photo'])                    
    assert not inferrer.is_valid_categorical(df['Age'])
    assert not inferrer.is_valid_categorical(df['Height'])    

    
def test_identifies_numerical(df):
    inferrer = TypeInferrer()
    assert inferrer.is_valid_numerical(df['Age'])
    assert inferrer.is_valid_numerical(df['Height'])    
    assert not inferrer.is_valid_numerical(df['City'])
    assert not inferrer.is_valid_numerical(df['Gender'])
    assert not inferrer.is_valid_numerical(df['Name'])
    assert not inferrer.is_valid_numerical(df['Photo'])                    


def test_identifies_binary(df):
    inferrer = TypeInferrer()
    assert inferrer.is_valid_binary(df['Gender'])    
    assert not inferrer.is_valid_binary(df['Age'])
    assert not inferrer.is_valid_binary(df['Height'])    
    assert not inferrer.is_valid_binary(df['City'])
    assert not inferrer.is_valid_binary(df['Name'])
    assert not inferrer.is_valid_binary(df['Photo'])                    
    
    
def test_identifies_image(df):
    inferrer = TypeInferrer()
    assert not inferrer.is_valid_image(df['Gender'])    
    assert not inferrer.is_valid_image(df['Age'])
    assert not inferrer.is_valid_image(df['Height'])    
    assert not inferrer.is_valid_image(df['City'])
    assert not inferrer.is_valid_image(df['Name'])
    assert inferrer.is_valid_image(df['Photo'])                    
    
    
def test_infer_types(df):
    inferrer = TypeInferrer(max_categories=3)
    assert inferrer.infer_datatype(df['Gender']) == 'binary'
    assert inferrer.infer_datatype(df['Age']) == 'numerical'
    assert inferrer.infer_datatype(df['Height']) == 'numerical'
    assert inferrer.infer_datatype(df['City']) == 'categorical'
    assert inferrer.infer_datatype(df['Name']) == 'text'
    assert inferrer.infer_datatype(df['Photo']) == 'image'           
    

def test_infer_datatypes(df):
    expected = {
        'Gender': 'binary',
        'Age': 'numerical',
        'Height': 'numerical',
        'City': 'categorical',
        'Name': 'text',
        'Photo': 'image'
    }
    inferrer = TypeInferrer(max_categories=3)
    actual = inferrer.infer_datatypes(df)
    assert actual == expected
    
