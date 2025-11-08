"""
Template library for the OMNIVID Motion Graphics Engine.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import asdict

from .core import EffectType, AnimationParameters, EngineMapping, AnimationEngine


class TemplateLibrary:
    """Manages a library of animation templates"""
    
    def __init__(self, templates_dir: str = None):
        """Initialize with optional templates directory"""
        self.templates: Dict[str, Dict] = {}
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def add_template(self, 
                    name: str, 
                    effect_type: EffectType,
                    engine: AnimationEngine,
                    config: Dict[str, Any],
                    preview_image: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> bool:
        """Add a new template to the library"""
        template = {
            "name": name,
            "effect_type": effect_type.value,
            "engine": engine.value,
            "config": config,
            "preview_image": preview_image or "",
            "tags": tags or [],
        }
        
        self.templates[name] = template
        return True
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def find_templates(self, 
                      effect_type: Optional[EffectType] = None,
                      engine: Optional[AnimationEngine] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Find templates matching criteria"""
        results = []
        
        for template in self.templates.values():
            # Filter by effect type
            if effect_type and template["effect_type"] != effect_type.value:
                continue
                
            # Filter by engine
            if engine and template["engine"] != engine.value:
                continue
                
            # Filter by tags
            if tags and not any(tag in template["tags"] for tag in tags):
                continue
                
            results.append(template)
            
        return results
    
    def apply_template(self, 
                      template_name: str, 
                      params: AnimationParameters) -> Dict[str, Any]:
        """Apply template to animation parameters"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Create a copy of the template config
        config = template["config"].copy()
        
        # Apply parameter overrides
        if "colors" in config and params.color_scheme:
            config["colors"] = params.color_scheme
            
        if "duration" in config:
            config["duration"] = params.duration
            
        if "intensity" in config:
            config["intensity"] = params.intensity
            
        if "easing" in config:
            config["easing"] = params.easing
            
        return config
    
    def save_template(self, name: str, output_path: Optional[str] = None) -> bool:
        """Save template to file"""
        if name not in self.templates:
            return False
            
        template = self.templates[name]
        output_path = output_path or os.path.join(
            self.templates_dir, f"{name.replace(' ', '_').lower()}.json"
        )
        
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
            
        return True
    
    def load_template(self, file_path: str) -> bool:
        """Load template from file"""
        try:
            with open(file_path, 'r') as f:
                template = json.load(f)
                
            # Validate required fields
            required = ["name", "effect_type", "engine", "config"]
            if not all(field in template for field in required):
                return False
                
            self.templates[template["name"]] = template
            return True
            
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def load_templates_from_dir(self, dir_path: Optional[str] = None) -> int:
        """Load all templates from a directory"""
        dir_path = dir_path or self.templates_dir
        count = 0
        
        for file_path in Path(dir_path).glob("*.json"):
            if self.load_template(str(file_path)):
                count += 1
                
        return count
    
    def generate_preview(self, 
                        template_name: str,
                        output_path: str,
                        width: int = 320,
                        height: int = 180) -> bool:
        """Generate a preview image for a template"""
        # This would typically use a headless browser or rendering engine
        # to generate a preview image of the animation
        # For now, this is a placeholder implementation
        try:
            # Create a simple preview image using PIL or similar
            from PIL import Image, ImageDraw
            import random
            
            img = Image.new('RGB', (width, height), (18, 18, 18))
            draw = ImageDraw.Draw(img)
            
            # Draw template info
            template = self.templates[template_name]
            draw.text((10, 10), template_name, fill=(255, 255, 255))
            draw.text((10, 30), f"Effect: {template['effect_type']}", fill=(200, 200, 200))
            draw.text((10, 50), f"Engine: {template['engine']}", fill=(200, 200, 200))
            
            # Draw a simple animation preview (just for demo)
            for _ in range(20):
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                draw.ellipse([x-5, y-5, x+5, y+5], fill=(r, g, b, 128))
            
            # Save the preview image
            img.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            return False
    
    def export_template(self, 
                       template_name: str,
                       output_format: str = "json") -> Optional[Union[str, bytes]]:
        """Export template in specified format"""
        if template_name not in self.templates:
            return None
            
        template = self.templates[template_name]
        
        if output_format.lower() == "json":
            return json.dumps(template, indent=2)
            
        elif output_format.lower() == "yaml":
            try:
                import yaml
                return yaml.dump(template)
            except ImportError:
                raise ImportError("PyYAML is required for YAML export")
                
        elif output_format.lower() == "python":
            # Generate Python code that creates this template
            code = f"""# {template_name} Template
from dataclasses import dataclass
from enum import Enum

class EffectType(Enum):
    {template['effect_type']} = "{template['effect_type']}"

class AnimationEngine(Enum):
    {template['engine']} = "{template['engine']}"

def create_template():
    return {{
        'name': {json.dumps(template['name'])},
        'effect_type': EffectType.{template['effect_type']},
        'engine': AnimationEngine.{template['engine']},
        'config': {json.dumps(template['config'], indent=4)},
        'tags': {json.dumps(template.get('tags', []))}
    }}
"""
            return code
            
        return None
