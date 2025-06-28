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
        """Generate CLI code from the given specification.
        
        Args:
            spec (str): The specification for generating the CLI
            
        Returns:
            str: The generated CLI code
        """
        # For now, just return a simple message that generation was successful
        # In a real implementation, this would parse the spec and generate code
        return f"Successfully generated CLI for: {spec}"

