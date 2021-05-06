# design the topic here for sending in for discourse

def _add_image_to_body(body, url_dict):

        for fil in url_dict:
            body += f"\n![{fil}]({url_dict[fil]})"
        return body

def create_topic(api, title, body, images):
    url_dict = {}
    def upload_files():
        for fl in images:
            filename = os.path.basename(fl)
            if Path(filename).suffix in ['jpg', 'jpeg', 'png', 'gif', 'heic', 'heif', 'webp']:
                response = api.upload_image(filename)
                url_dict[fl] = response.short_url
            else:
                raise ValueError("File format not supported, Supported format are- jpg, jpeg, png, gif, heic, heif, webp")

    body_w_images = _add_image_to_body(body, url_dict)
    return api.create_post(title, body_w_images)