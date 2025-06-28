import os
from jinja2 import Environment, FileSystemLoader

class CLIGenerator:
    def __init__(self, template_dir=None):
        if template_dir is None:
            # Szablony są teraz w text2api/generators/templates
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_cli(self, api_spec):
        template = self.env.get_template('cli.py.j2')
        return template.render(api_spec=api_spec)

    def render_requirements(self, api_spec):
        template = self.env.get_template('requirements.txt.j2')
        return template.render(api_spec=api_spec)

    def render_readme(self, api_spec):
        template = self.env.get_template('README.md.j2')
        return template.render(api_spec=api_spec)

    def generate(self, spec):
        """Generate CLI code from the given specification and write to file.
        
        Args:
            spec (str): The specification for generating the CLI
            
        Returns:
            str: A success message with the path to the generated file
        """
        # Create output directory if it doesn't exist
        output_dir = "generated_apis/twoja_specyfikacja_api"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a simple API spec from the input text
        # In a real implementation, this would parse the spec more intelligently
        api_name = "".join(x.capitalize() for x in spec.split() if x.isalnum())
        api_spec = {
            "name": api_name or "GeneratedAPI",
            "models": [
                {"name": "Product", "fields": ["id", "name", "category", "price"]},
                {"name": "Category", "fields": ["id", "name", "description"]}
            ]
        }
        
        # Generate the CLI code
        cli_code = self.render_cli(api_spec)
        
        # Write the generated code to a file
        output_file = os.path.join(output_dir, "cli.py")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cli_code)
            
        return f"Successfully generated CLI at: {output_file}"

