const replacements = {
    "á": "a",
    "à": "a",
    "é": "e",
    "è": "e",
    "í": "i",
    "ì": "i",
    "ó": "o",
    "ò": "o",
    "ú": "u",
    "ù": "u",
    "ñ": "n",
    "ç": "c",
    " ": "_",
};

export function normalizeCityName(name: string) {
    name = name.toLocaleLowerCase("en-US");

    for (const [key, value] of Object.entries(replacements)) {
        name = name.replaceAll(key, value);
    }

    name = name[0].toLocaleUpperCase("en-US") + name.substring(1); 
    return name
}
