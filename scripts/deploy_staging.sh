export AZURE_STORAGE_ACCOUNT="storeanton"
export AZURE_STORAGE_KEY="DkMr0n+RyawwpQWgA6pwLytfcRp+b/ci9SOmWEdM3hxIh6Y+YWA/U7QocYeyQzCgGHPJTbTd569EZ6RXnChcjw=="
export AZURE_SHARE_NAME="myshare"

# Working directory will be: $(System.DefaultWorkingDirectory)/test_percepti

for file_name in images_ubuntu/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "staging_$file_name"
done


for file_name in images_windows/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "staging_$file_name"
done

for file_name in images_osx/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "staging_$file_name"
done



