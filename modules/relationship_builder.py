"""
Relationship Builder
Discovers and creates relationships between Salesforce objects
"""

class RelationshipBuilder:
    
    def discover_relationships(self, sf, object_name):
        """Discover relationships for an object"""
        try:
            desc = sf.__getattr__(object_name).describe()
            relationships = {
                'parent_relationships': [],
                'child_relationships': []
            }
            
            # Get parent relationships (lookup/master-detail fields)
            for field in desc['fields']:
                if field['type'] == 'reference' and field['referenceTo']:
                    relationships['parent_relationships'].append({
                        'field': field['name'],
                        'label': field['label'],
                        'relatedObject': field['referenceTo'][0] if field['referenceTo'] else None,
                        'required': not field['nillable']
                    })
            
            # Get child relationships
            for rel in desc['childRelationships']:
                if rel['relationshipName']:
                    relationships['child_relationships'].append({
                        'relationshipName': rel['relationshipName'],
                        'childObject': rel['childSObject'],
                        'field': rel['field']
                    })
            
            return relationships
        except Exception as e:
            raise Exception(f"Failed to discover relationships: {str(e)}")
    
    def create_relationship(self, sf, parent_object, parent_id, child_object, relationship_field, additional_data=None):
        """Create a relationship between two records"""
        try:
            data = {relationship_field: parent_id}
            
            if additional_data:
                data.update(additional_data)
            
            result = sf.__getattr__(child_object).create(data)
            return result
        except Exception as e:
            raise Exception(f"Failed to create relationship: {str(e)}")
    
    def get_relationship_graph(self, sf, object_name, depth=2):
        """Get relationship graph data for visualization"""
        try:
            nodes = []
            edges = []
            visited = set()
            
            def explore(obj_name, current_depth):
                if current_depth > depth or obj_name in visited:
                    return
                
                visited.add(obj_name)
                nodes.append({
                    'id': obj_name,
                    'label': obj_name,
                    'type': 'object'
                })
                
                try:
                    rels = self.discover_relationships(sf, obj_name)
                    
                    # Add parent relationships
                    for rel in rels['parent_relationships']:
                        if rel['relatedObject']:
                            edges.append({
                                'source': obj_name,
                                'target': rel['relatedObject'],
                                'label': rel['field'],
                                'type': 'lookup'
                            })
                            if current_depth < depth:
                                explore(rel['relatedObject'], current_depth + 1)
                    
                    # Add child relationships
                    for rel in rels['child_relationships']:
                        edges.append({
                            'source': obj_name,
                            'target': rel['childObject'],
                            'label': rel['relationshipName'],
                            'type': 'child'
                        })
                        if current_depth < depth:
                            explore(rel['childObject'], current_depth + 1)
                except:
                    pass
            
            explore(object_name, 0)
            
            return {
                'nodes': nodes,
                'edges': edges
            }
        except Exception as e:
            raise Exception(f"Failed to build relationship graph: {str(e)}")


