import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initializes the service for uploading files to Cloudinary.

        Arguments:
            cloud_name: The cloud name in Cloudinary.
            api_key: The API key for accessing Cloudinary.
            api_secret: The API secret for accessing Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        # Configures Cloudinary for file uploads.
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантажує файл на Cloudinary і генерує URL для доступу до зображення.

        Формує унікальний ідентифікатор для користувача і завантажує файл на сервер.
        Після успішного завантаження повертає URL зображення з певними параметрами (розмір, обрізка).

        Аргументи:
            file: Файл для завантаження.
            username: Ім'я користувача для формування унікального public_id.

        Повертає:
            str: URL зображення, доступного на Cloudinary.
        """
        # Creates a unique public_id for the user.
        public_id = f"RestApp/{username}"
        # Uploads a file to the Cloudinary server.
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        # Forms a URL to access the image with the appropriate dimensions.
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
