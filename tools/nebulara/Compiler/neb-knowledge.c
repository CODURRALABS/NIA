/*
 * neb-knowledge.c - Knowledge Graph Module
 * 
 * AI-native knowledge storage and retrieval:
 * - Entity-Relationship model
 * - Graph traversal
 * - Semantic search
 * - Context-aware retrieval
 *
 * Build: gcc -o neb-knowledge.exe neb-knowledge.c -static -O2
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Knowledge types */
typedef enum {
    KNOW_TYPE_ENTITY,
    KNOW_TYPE_RELATION,
    KNOW_TYPE_FACT,
    KNOW_TYPE_RULE,
    KNOW_TYPE_CONTEXT
} KnowType;

/* Entity in the knowledge graph */
typedef struct {
    int id;
    char name[256];
    char type[128];        /* e.g., "function", "variable", "concept" */
    char value[512];
    int relations[64];     /* IDs of connected entities */
    int relation_count;
    int confidence;        /* 0-100 */
} Entity;

/* Knowledge graph */
typedef struct {
    Entity entities[4096];
    int count;
} KnowledgeGraph;

static KnowledgeGraph graph;

/* Initialize the knowledge graph */
void kg_init(void) {
    graph.count = 0;
}

/* Add an entity */
int kg_add_entity(const char *name, const char *type, const char *value, int confidence) {
    if (graph.count >= 4096) return -1;
    
    Entity *e = &graph.entities[graph.count];
    e->id = graph.count;
    strncpy(e->name, name, 255);
    strncpy(e->type, type, 127);
    strncpy(e->value, value, 511);
    e->relation_count = 0;
    e->confidence = confidence;
    graph.count++;
    
    return e->id;
}

/* Add a relation between two entities */
int kg_add_relation(int from_id, int to_id) {
    if (from_id < 0 || from_id >= graph.count) return -1;
    if (to_id < 0 || to_id >= graph.count) return -2;
    
    Entity *e = &graph.entities[from_id];
    if (e->relation_count >= 64) return -3;
    
    e->relations[e->relation_count++] = to_id;
    return 0;
}

/* Find entity by name */
Entity *kg_find(const char *name) {
    for (int i = 0; i < graph.count; i++) {
        if (strcmp(graph.entities[i].name, name) == 0) {
            return &graph.entities[i];
        }
    }
    return NULL;
}

/* Find all entities of a type */
int kg_find_by_type(const char *type, Entity **results, int max_results) {
    int count = 0;
    for (int i = 0; i < graph.count && count < max_results; i++) {
        if (strcmp(graph.entities[i].type, type) == 0) {
            results[count++] = &graph.entities[i];
        }
    }
    return count;
}

/* Semantic search - find entities matching a query */
int kg_search(const char *query, Entity **results, int max_results) {
    int count = 0;
    for (int i = 0; i < graph.count && count < max_results; i++) {
        if (strstr(graph.entities[i].name, query) ||
            strstr(graph.entities[i].value, query)) {
            results[count++] = &graph.entities[i];
        }
    }
    return count;
}

/* Get related entities */
int kg_get_related(int entity_id, Entity **results, int max_results) {
    if (entity_id < 0 || entity_id >= graph.count) return 0;
    
    Entity *e = &graph.entities[entity_id];
    int count = 0;
    for (int i = 0; i < e->relation_count && count < max_results; i++) {
        results[count++] = &graph.entities[e->relations[i]];
    }
    return count;
}

/* Get context - all entities in a scope/context */
int kg_get_context(const char *context, Entity **results, int max_results) {
    int count = 0;
    for (int i = 0; i < graph.count && count < max_results; i++) {
        if (strcmp(graph.entities[i].type, context) == 0 ||
            strstr(graph.entities[i].name, context)) {
            results[count++] = &graph.entities[i];
        }
    }
    return count;
}

/* Print entity */
void kg_print_entity(Entity *e) {
    printf("  [%d] %s (%s) = %s (confidence: %d%%)\n",
           e->id, e->name, e->type, e->value, e->confidence);
    if (e->relation_count > 0) {
        printf("      relations: ");
        for (int i = 0; i < e->relation_count; i++) {
            printf("%d ", e->relations[i]);
        }
        printf("\n");
    }
}

/* Print the entire knowledge graph */
void kg_print(void) {
    printf("=== Knowledge Graph (%d entities) ===\n", graph.count);
    for (int i = 0; i < graph.count; i++) {
        kg_print_entity(&graph.entities[i]);
    }
    printf("=== End Knowledge Graph ===\n");
}

/* Demo */
int main(int argc, char *argv[]) {
    printf("=== Nebulara Knowledge Graph Module ===\n\n");
    
    kg_init();
    
    /* Add some entities */
    int func_add = kg_add_entity("add", "function", "int add(int, int) -> int", 100);
    int func_print = kg_add_entity("PRINT", "builtin", "print to stdout", 100);
    int param_a = kg_add_entity("a", "parameter", "first argument to add", 100);
    int param_b = kg_add_entity("b", "parameter", "second argument to add", 100);
    int lang_neb = kg_add_entity("Nebulara", "language", "AI-native programming language", 100);
    
    /* Add relations */
    kg_add_relation(func_add, param_a);
    kg_add_relation(func_add, param_b);
    kg_add_relation(param_a, lang_neb);
    kg_add_relation(param_b, lang_neb);
    
    /* Print graph */
    kg_print();
    
    /* Search */
    printf("\nSearch 'add':\n");
    Entity *results[10];
    int count = kg_search("add", results, 10);
    for (int i = 0; i < count; i++) {
        kg_print_entity(results[i]);
    }
    
    /* Find by type */
    printf("\nAll functions:\n");
    count = kg_find_by_type("function", results, 10);
    for (int i = 0; i < count; i++) {
        kg_print_entity(results[i]);
    }
    
    /* Get related */
    printf("\nRelated to 'add':\n");
    count = kg_get_related(func_add, results, 10);
    for (int i = 0; i < count; i++) {
        kg_print_entity(results[i]);
    }
    
    printf("\nKnowledge graph module: OK\n");
    return 0;
}
