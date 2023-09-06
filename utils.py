def get_numerated_list(lst : list) -> list:
    result = []
    for index, row in enumerate(lst):
        result.append(f'{index+1}. {row}')
    return result

def get_numerated_list_string(lst : list) -> str:
    result = get_numerated_list(lst)
    return '\n'.join(result)

def get_fixed_json(text : str) -> str:
    text = text.replace(", ]", "]").replace(",]", "]").replace(",\n]", "]")
    open_bracket = min(text.find('['), text.find('{'))
    if open_bracket == -1:
        return text
            
    close_bracket = max(text.rfind(']'), text.rfind('}'))
    if close_bracket == -1:
        return text
    return text[open_bracket:close_bracket+1]
