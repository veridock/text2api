"""
Generator dla gRPC API
"""

import os
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment

from ..core.analyzer import ApiSpec
from ..utils.file_utils import FileManager


class GRPCGenerator:
    """Generator kodu gRPC"""

    def __init__(self):
        self.file_manager = FileManager()
        self.templates = self._load_templates()

    def _get_docstring(self, text: str) -> str:
        """Get a docstring for a method."""
        return f'"""{text}"""'

    def _load_templates(self) -> Dict[str, str]:
        """Ładuje szablony Jinja2 dla gRPC"""
        proto_template = """syntax = "proto3";

package {{ api_spec.name.lower() }};

// The {{ api_spec.name }} service definition.
service {{ api_spec.name }}Service {
    // Ping endpoint for health checks
    rpc Ping (PingRequest) returns (PingResponse) {}
    
    // Add your gRPC methods here
    {% for model in api_spec.models %}
    rpc Create{{ model.name }} (Create{{ model.name }}Request) returns ({{ model.name }}Response) {}
    rpc Get{{ model.name }} (Get{{ model.name }}Request) returns ({{ model.name }}Response) {}
    rpc List{{ model.name }}s (List{{ model.name }}sRequest) returns (List{{ model.name }}sResponse) {}
    rpc Update{{ model.name }} (Update{{ model.name }}Request) returns ({{ model.name }}Response) {}
    rpc Delete{{ model.name }} (Delete{{ model.name }}Request) returns (Delete{{ model.name }}Response) {}
    {% endfor %}
}

// Common responses
message PingRequest {
    string message = 1;
}

message PingResponse {
    string message = 1;
    string status = 2;
}

// Model definitions
{% for model in api_spec.models %}
message {{ model.name }} {
    string id = 1;
    {% for field in model.fields %}
    {{ self.get_proto_type(field.type) }} {{ field.name }} = {{ loop.index + 1 }};
    {% endfor %}
    string created_at = {{ model.fields|length + 2 }};
    string updated_at = {{ model.fields|length + 3 }};
}

// {{ model.name }} request/response messages
message Create{{ model.name }}Request {
    {{ model.name }} {{ model.name|lower }} = 1;
}

message Get{{ model.name }}Request {
    string id = 1;
}

message List{{ model.name }}sRequest {
    int32 page_size = 1;
    string page_token = 2;
}

message Update{{ model.name }}Request {
    {{ model.name }} {{ model.name|lower }} = 1;
}

message Delete{{ model.name }}Request {
    string id = 1;
}

message {{ model.name }}Response {
    bool success = 1;
    string message = 2;
    {{ model.name }} {{ model.name|lower }} = 3;
}

message List{{ model.name }}sResponse {
    repeated {{ model.name }} {{ model.name|lower }}s = 1;
    string next_page_token = 2;
}

message Delete{{ model.name }}Response {
    bool success = 1;
    string message = 2;
}

{% endfor %}
"""

        server_template = """# gRPC server generated by text2api

import os
import grpc
from concurrent import futures
import logging
from datetime import datetime
from typing import Dict, List

import {{ api_spec.name.lower() }}_pb2
import {{ api_spec.name.lower() }}_pb2_grpc

class {{ api_spec.name }}Service({{ api_spec.name.lower() }}_pb2_grpc.{{ api_spec.name }}ServiceServicer):
    # Implementation of {{ api_spec.name }}Service
    pass
    
    def __init__(self):
        self.db: Dict[str, Dict] = {}
    
    def Ping(self, request, context):
        # Simple health check endpoint
        return {{ api_spec.name.lower() }}_pb2.PingResponse(
            message=f"Pong: {request.message}",
            status="SERVING"
        )
    
    # Add your service method implementations here
    {% for model in api_spec.models %}
    def Create{{ model.name }}(self, request, context):
        # Create a new {{ model.name }} record
        try:
            item = request.{{ model.name|lower }}
            item_id = str(len(self.db) + 1)
            item_dict = {
                'id': item_id,
                {% for field in model.fields %}
                '{{ field.name }}': item.{{ field.name }},
                {% endfor %}
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            self.db[item_id] = item_dict
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=True,
                message="{{ model.name }} created successfully",
                {{ model.name|lower }}={{ api_spec.name.lower() }}_pb2.{{ model.name }}(
                    id=item_id,
                    {% for field in model.fields %}
                    {{ field.name }}=item_dict['{{ field.name }}'],
                    {% endfor %}
                    created_at=item_dict['created_at'],
                    updated_at=item_dict['updated_at']
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=False,
                message=f"Error creating {{ model.name|lower }}: {str(e)}"
            )
    
    def Get{{ model.name }}(self, request, context):
        # Get a {{ model.name }} by ID
        try:
            item_id = request.id
            if item_id not in self.db:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                    success=False,
                    message="{{ model.name }} not found"
                )
            
            item = self.db[item_id]
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=True,
                message="{{ model.name }} retrieved successfully",
                {{ model.name|lower }}={{ api_spec.name.lower() }}_pb2.{{ model.name }}(
                    id=item_id,
                    {% for field in model.fields %}
                    {{ field.name }}=item['{{ field.name }}'],
                    {% endfor %}
                    created_at=item['created_at'],
                    updated_at=item['updated_at']
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=False,
                message=f"Error retrieving {{ model.name|lower }}: {str(e)}"
            )
    
    def List{{ model.name }}s(self, request, context):
        # List all {{ model.name }} records
        try:
            items = []
            for item_id, item in self.db.items():
                items.append({{ api_spec.name.lower() }}_pb2.{{ model.name }}(
                    id=item_id,
                    {% for field in model.fields %}
                    {{ field.name }}=item['{{ field.name }}'],
                    {% endfor %}
                    created_at=item['created_at'],
                    updated_at=item['updated_at']
                ))
            
            return {{ api_spec.name.lower() }}_pb2.List{{ model.name }}sResponse(
                {{ model.name|lower }}s=items
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {{ api_spec.name.lower() }}_pb2.List{{ model.name }}sResponse()
    
    def Update{{ model.name }}(self, request, context):
        # Update a {{ model.name }} record
        try:
            item = request.{{ model.name|lower }}
            item_id = item.id
            
            if item_id not in self.db:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                    success=False,
                    message="{{ model.name }} not found"
                )
            
            updated_item = {
                'id': item_id,
                {% for field in model.fields %}
                '{{ field.name }}': item.{{ field.name }},
                {% endfor %}
                'created_at': self.db[item_id]['created_at'],
                'updated_at': datetime.utcnow().isoformat()
            }
            self.db[item_id] = updated_item
            
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=True,
                message="{{ model.name }} updated successfully",
                {{ model.name|lower }}={{ api_spec.name.lower() }}_pb2.{{ model.name }}(
                    id=item_id,
                    {% for field in model.fields %}
                    {{ field.name }}=updated_item['{{ field.name }}'],
                    {% endfor %}
                    created_at=updated_item['created_at'],
                    updated_at=updated_item['updated_at']
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {{ api_spec.name.lower() }}_pb2.{{ model.name }}Response(
                success=False,
                message=f"Error updating {{ model.name|lower }}: {str(e)}"
            )
    
    def Delete{{ model.name }}(self, request, context):
        # Delete a {{ model.name }} record
        try:
            item_id = request.id
            if item_id not in self.db:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return {{ api_spec.name.lower() }}_pb2.Delete{{ model.name }}Response(
                    success=False,
                    message="{{ model.name }} not found"
                )
            
            del self.db[item_id]
            return {{ api_spec.name.lower() }}_pb2.Delete{{ model.name }}Response(
                success=True,
                message="{{ model.name }} deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {{ api_spec.name.lower() }}_pb2.Delete{{ model.name }}Response(
                success=False,
                message=f"Error deleting {{ model.name|lower }}: {str(e)}"
            )
    
    {% endfor %}

def serve():
    # Start the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    {{ api_spec.name.lower() }}_pb2_grpc.add_{{ api_spec.name }}ServiceServicer_to_server(
        {{ api_spec.name }}Service(), server)
    
    port = os.getenv('GRPC_PORT', '50051')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server started on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
"""

        return {"proto": proto_template, "server.py": server_template}

    def get_proto_type(self, field_type: str) -> str:
        """Map Python types to Protocol Buffer types"""
        type_mapping = {
            "string": "string",
            "int": "int32",
            "float": "float",
            "bool": "bool",
            "bytes": "bytes",
        }
        return type_mapping.get(field_type, "string")

    async def generate(self, api_spec: ApiSpec, output_path: Path) -> Dict[str, str]:
        """
        Generuje kod gRPC na podstawie specyfikacji API

        Args:
            api_spec: Specyfikacja API
            output_path: Ścieżka do katalogu wyjściowego

        Returns:
            Słownik zawierający wygenerowane pliki
        """
        generated_files = {}
        env = Environment()

        # Create output directories
        proto_dir = output_path / "protos"
        proto_dir.mkdir(parents=True, exist_ok=True)

        # Generate .proto file
        proto_template = env.from_string(self.templates["proto"])
        proto_content = proto_template.render(
            api_spec=api_spec, self={"get_proto_type": self.get_proto_type}
        )

        proto_file = proto_dir / f"{api_spec.name.lower()}.proto"
        await self.file_manager.write_file(proto_file, proto_content)
        generated_files["proto"] = str(proto_file)

        # Generate server.py
        server_template = env.from_string(self.templates["server.py"])
        server_content = server_template.render(
            api_spec=api_spec, self={"get_proto_type": self.get_proto_type}
        )

        server_file = output_path / "server.py"
        await self.file_manager.write_file(server_file, server_content)
        generated_files["server.py"] = str(server_file)

        # Generate requirements.txt
        requirements = [
            "grpcio>=1.54.0",
            "grpcio-tools>=1.54.0",
            "protobuf>=4.22.0",
        ]

        requirements_file = output_path / "requirements.txt"
        await self.file_manager.write_file(
            requirements_file, "\n".join(requirements) + "\n"
        )
        generated_files["requirements.txt"] = str(requirements_file)

        # Generate README.md
        readme_content = f"""# {api_spec.name} gRPC Service

This is an auto-generated gRPC service for {api_spec.name}.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate gRPC code:
   ```bash
   python -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. protos/{api_spec.name.lower()}.proto
   ```

3. Run the server:
   ```bash
   python server.py
   ```

## API Documentation

### Methods

#### Ping
- Request: `PingRequest`
- Response: `PingResponse`
- Description: Health check endpoint

"""

        readme_file = output_path / "README.md"
        await self.file_manager.write_file(readme_file, readme_content)
        generated_files["README.md"] = str(readme_file)

        # Generate compile script
        compile_script = f"""#!/bin/bash
# Script to compile gRPC code

python -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. protos/{api_spec.name.lower()}.proto
"""

        script_path = output_path / "compile_proto.sh"
        await self.file_manager.write_file(script_path, compile_script)
        generated_files["compile_proto.sh"] = str(script_path)

        return generated_files
