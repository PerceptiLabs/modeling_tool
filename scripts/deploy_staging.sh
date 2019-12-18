export AZURE_STORAGE_ACCOUNT="plabsdevopsstorage"
export AZURE_STORAGE_KEY="50Vj8cOQnjiFqAqnzVXGJT1wCGsNpHUP2fZqWBWhE3w2EtyU8Js9Wpih/J7LdTHz1PI+CYwMtOaS94bC1seLqQ=="
export AZURE_SHARE_NAME="myshare"

# Working directory will be: $(System.DefaultWorkingDirectory)/test_percepti

dir

for file_name in images_ubuntu/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "$file_name" --path "staging_$file_name"
done


for file_name in images_windows/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "$file_name" --path "staging_$file_name"
done

for file_name in images_osx/*
do
  az storage file upload --share-name $AZURE_SHARE_NAME --source "$file_name" --path "staging_$file_name"
done



