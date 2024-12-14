from apps.utils import generate_audio_from_excel

excel_file_path = "vocabs.xlsx"
output_directory = "media/vocab/audio"
generate_audio_from_excel(excel_file_path, output_directory)

