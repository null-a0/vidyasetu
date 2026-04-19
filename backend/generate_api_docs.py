import json

def get_ref_schema(ref, components):
    name = ref.split('/')[-1]
    return components.get('schemas', {}).get(name, {})

def format_schema(schema, components, level=0):
    if not schema:
        return 'Any'
    if '$ref' in schema:
        ref_schema = get_ref_schema(schema['$ref'], components)
        return format_schema(ref_schema, components, level)
    
    # Check if there is an anyOf/allOf
    if 'anyOf' in schema:
        return ' | '.join([format_schema(s, components, level) for s in schema['anyOf']])
    if 'allOf' in schema:
        return ' & '.join([format_schema(s, components, level) for s in schema['allOf']])
    
    _type = schema.get('type', 'object')
    
    if _type == 'object':
        props = schema.get('properties', {})
        if not props:
            return 'dict'
        lines = []
        indent = '  ' * level
        for k, v in props.items():
            req = '*' if k in schema.get('required', []) else ''
            lines.append(f'{indent}- **{k}**{req}: {format_schema(v, components, level+1)}')
        return '\n' + '\n'.join(lines)
    elif _type == 'array':
        items = schema.get('items', {})
        return f'Array of [{format_schema(items, components, level).strip()}]'
    else:
        return _type

def main():
    with open('openapi.json', 'r', encoding='utf-8') as f:
        spec = json.load(f)

    md = ['# VidyaSetu API Documentation\n']

    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            md.append(f'## {method.upper()} {path}')
            
            summary = op.get('summary', '')
            if summary:
                md.append(f'**Summary**: {summary}\n')
            
            # Parameters (path, query)
            params = op.get('parameters', [])
            if params:
                md.append('### Parameters')
                for p in params:
                    req = '*' if p.get('required') else ''
                    schema_type = p.get('schema', {}).get('type', 'string')
                    md.append(f'- **{p.get("name")}**{req} ({p.get("in")}): {schema_type}')
                md.append('')
                    
            # Request Body
            body = op.get('requestBody', {})
            if body:
                content = body.get('content', {})
                json_schema = content.get('application/json', {}).get('schema', {})
                form_schema = content.get('multipart/form-data', {}).get('schema', {})
                
                target_schema = json_schema or form_schema
                if target_schema:
                    md.append('### Request Body')
                    md.append(format_schema(target_schema, spec.get('components', {})))
                    md.append('')

            # Responses (just looking at 200/201)
            resps = op.get('responses', {})
            success_resp = resps.get('200') or resps.get('201') or resps.get('204')
            if success_resp:
                content = success_resp.get('content', {})
                if 'application/json' in content:
                    resp_schema = content['application/json'].get('schema', {})
                    if resp_schema:
                        md.append('### Response: 200/201 (JSON)')
                        md.append(format_schema(resp_schema, spec.get('components', {})))
                        md.append('')
                else:
                    md.append('### Response: No Content or File')
                    md.append('')
                
            md.append('---\n')

    with open('API_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

if __name__ == '__main__':
    main()
