'''
このpyファイルは"firestore-key.json"をgitの".streamlit/secrets.toml"に書き出すものです
".streamlit/secrets.toml"の内容をstreamlitのsecretに貼り付けてください
一度使った後は、"firestore-key.json"ないし".streamlit/secrets.toml"は削除してください
'''
import toml

output_file = ".streamlit/secrets.toml"

with open("firestore-key.json") as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open(output_file, "w") as target:
    target.write(toml_config)
