# 🎮 Playground: Visual Multi-Agent Workflow Builder

## 🎉 Feature Overview

The **Playground** is a powerful visual interface for creating multi-agent LLM workflows using drag-and-drop. Build complex DAG (Directed Acyclic Graph) pipelines where different models process data sequentially or in parallel!

---

## 🌟 Key Features

### 1. **Visual Workflow Builder**
- Drag and drop models onto a canvas
- Connect models with edges to define data flow
- Create complex DAG workflows visually
- Real-time canvas manipulation

### 2. **Multi-Agent Pipelines**
- Use multiple LLM models in one workflow
- Models can be the same or different
- Sequential or parallel execution
- Automatic topological sorting

### 3. **Custom Prompts per Node**
- Edit prompt template for each model
- Use variables: `{input}` and `{node-id}`
- Dynamic prompt building with predecessor outputs
- Real-time prompt preview

### 4. **Intelligent Execution**
- Validates DAG (detects cycles)
- Executes in correct topological order
- Parallel execution of independent nodes
- Shows results for each node

### 5. **Save & Load Workflows**
- Export workflows as JSON
- Import saved workflows
- Share workflows with others
- Reusable pipeline templates

---

## 🎨 User Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [Model Palette]  [Main Canvas with Controls]  [Results/Editor]  │
│                                                                   │
│  Available       ┌─────────────────────────┐     Node Editor    │
│  Models:         │  Input: [_________] [▶] │     or             │
│                  │                         │     Execution      │
│  [GPT-2]         │  ┌────┐    ┌────┐      │     Results        │
│  [Qwen]          │  │ N1 │───→│ N2 │      │                    │
│  [Embed]         │  └────┘    └────┘      │                    │
│                  │                         │                    │
│  + Info Box      └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Left Sidebar: Model Palette
- Shows all **running** models
- Click to add model node to canvas
- Real-time updates every 5 seconds
- Displays model type (Chat/Embedding)

### Center: Main Canvas
- **Controls Bar**: Input field, Run, Clear, Save, Load
- **React Flow Canvas**: Visual workflow builder
  - Drag nodes to reposition
  - Connect nodes by dragging from handles
  - Zoom and pan controls
  - Dot grid background
  - Node/edge counter

### Right Sidebar: Dynamic Panel
- **Node Editor** (when node selected): Edit prompt templates
- **Execution Results** (after running): See outputs from each node
- **Empty State** (default): Instructions and status

---

## 🎯 How to Use

### Step 1: Deploy Models
Before using Playground, deploy at least 1 running model:

```
Dashboard → Deploy → Choose Model → Deploy
```

Wait for status to be **RUNNING** ✅

### Step 2: Add Nodes
1. Go to **Playground** tab
2. See available models in left sidebar
3. Click a model to add it to canvas
4. Repeat to add more models

### Step 3: Connect Nodes
1. Find the **green dot** (output handle) on a node
2. **Drag** from green dot to **blue dot** (input handle) of another node
3. An edge appears connecting the nodes
4. Create any DAG structure you want!

**Example Flow:**
```
Node A (Analyzer) → Node B (Summarizer) → Node C (Formatter)
```

### Step 4: Edit Prompts
1. Click **"Edit"** button on any node
2. Right sidebar shows prompt editor
3. Modify the prompt template
4. Use variables:
   - `{input}` - Original user input
   - `{node-a-id}` - Output from Node A
5. Click **"Update"** to save

**Example Prompts:**

**Node 1 (Analyzer):**
```
Analyze the sentiment of this text: {input}
Return ONLY: positive, negative, or neutral
```

**Node 2 (Explainer):**
```
The sentiment is: {node-1}
Now explain why the text has this sentiment: {input}
```

### Step 5: Run Workflow
1. Enter input text in the top input field
2. Click **▶ Run** button
3. Watch execution (may take 10-30s on CPU)
4. See results in right sidebar!

---

## 📊 Example Workflows

### Example 1: Simple Chain (A → B)

**Setup:**
- Node A: GPT-2 (ID: `analyzer`)
- Node B: GPT-2 (ID: `summarizer`)
- Edge: A → B

**Prompts:**
- Node A: `Analyze this text: {input}. What is the main topic?`
- Node B: `Based on this analysis: {analyzer}, write a one-sentence summary`

**Input:** `"Artificial intelligence is transforming healthcare"`

**Execution Flow:**
```
User Input
    ↓
Node A: "The main topic is AI in healthcare"
    ↓
Node B: "AI is revolutionizing the medical industry"
```

---

### Example 2: Parallel Processing (A & B → C)

**Setup:**
- Node A: GPT-2 (ID: `sentiment`)
- Node B: GPT-2 (ID: `topic`)
- Node C: GPT-2 (ID: `combiner`)
- Edges: A → C, B → C

**Prompts:**
- Node A: `What's the sentiment of: {input}? (positive/negative/neutral)`
- Node B: `What's the main topic of: {input}? (one word)`
- Node C: `Sentiment: {sentiment}, Topic: {topic}. Write a categorized summary.`

**Input:** `"I love how AI is revolutionizing education!"`

**Execution Flow:**
```
             User Input
            /          \
           /            \
     Node A              Node B
   (Sentiment)          (Topic)
   "positive"          "education"
           \            /
            \          /
             Node C
          (Combiner)
  "Positive sentiment about AI in education..."
```

**Note:** Nodes A and B execute **in parallel** (same layer), then C executes after both complete!

---

### Example 3: Complex DAG (Multi-Stage)

**Setup:**
- Node A: Analyzer
- Node B: Extractor
- Node C: Validator (depends on A & B)
- Node D: Formatter (depends on C)

**Graph:**
```
     A ──┐
         ├──→ C ──→ D
     B ──┘
```

**Execution Layers:**
1. Layer 1: A, B (parallel)
2. Layer 2: C (waits for A & B)
3. Layer 3: D (waits for C)

---

## 🔧 Prompt Template Variables

### Available Variables

1. **`{input}`** - Original user input
   ```
   Example: "Analyze: {input}"
   Input: "Hello world"
   Result: "Analyze: Hello world"
   ```

2. **`{node-id}`** - Output from predecessor node
   ```
   Example: "Based on {analyzer}, suggest improvements"
   If node "analyzer" output: "Positive sentiment"
   Result: "Based on Positive sentiment, suggest improvements"
   ```

### Multi-Variable Example

**Node Prompt:**
```
Original input: {input}
Sentiment analysis: {sentiment-node}
Topic extraction: {topic-node}
Now combine these insights.
```

---

## 🎮 Canvas Controls

### Mouse Actions
- **Left Click**: Select node/edge
- **Left Drag**: Move node or canvas (if empty space)
- **Right Drag**: Pan canvas
- **Scroll**: Zoom in/out

### Control Panel
- **🔍 +/-**: Zoom controls
- **⊡**: Fit view (auto-zoom to see all nodes)
- **🔒**: Lock/unlock nodes (prevent moving)

### Toolbar Buttons
- **▶ Run**: Execute workflow
- **🗑️**: Clear entire canvas
- **⬇️**: Save workflow as JSON
- **⬆️**: Load workflow from JSON

---

## 💾 Save & Load

### Save Workflow
1. Click **Download** button (⬇️)
2. Workflow saved as `workflow-{timestamp}.json`
3. Contains all nodes, edges, prompts, and positions

### Load Workflow
1. Click **Upload** button (⬆️)
2. Select a `.json` workflow file
3. Canvas restored with all nodes and connections

### Workflow JSON Structure
```json
{
  "nodes": [
    {
      "id": "node-123",
      "type": "modelNode",
      "position": {"x": 100, "y": 100},
      "data": {
        "modelId": "gpt2-456",
        "modelName": "GPT-2",
        "promptTemplate": "Analyze: {input}"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-123",
      "target": "node-456"
    }
  ]
}
```

---

## ⚡ Execution Details

### Workflow Validation
Before execution, the system checks:
- ✅ Workflow is a valid DAG (no cycles)
- ✅ All models are running
- ✅ All edge references are valid

If validation fails, you'll see an error:
- "Workflow contains cycles (not a valid DAG)"
- "Model {id} is not running"

### Execution Order
The workflow engine uses **topological sorting** to determine execution order:

**Example:**
```
Graph: A → C, B → C, C → D

Layers:
1. [A, B] - Execute in parallel
2. [C]    - Wait for A and B
3. [D]    - Wait for C
```

### Parallel Execution
Nodes in the same layer run **concurrently** for better performance!

---

## 📊 Execution Results

After running a workflow, the right sidebar shows results for each node:

```
┌─────────────────────────┐
│ Execution Results       │
│ ✓ Completed in 12.34s   │
├─────────────────────────┤
│ node-123          2.5s  │
│ ┌─────────────────────┐ │
│ │ Output text here... │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ node-456          3.2s  │
│ ┌─────────────────────┐ │
│ │ Output text here... │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

Each node shows:
- Node ID
- Execution time
- Output text (scrollable)
- Error message (if failed)

---

## 🚨 Common Issues & Solutions

### Issue 1: "No models available"
**Solution:** Deploy at least one model from Dashboard → Deploy

### Issue 2: "Workflow contains cycles"
**Solution:** Check your edges - you have a circular dependency. Remove edge to break cycle.

**Example of Cycle:**
```
A → B → C → A  ❌ (Cycle!)
```

**Fix:**
```
A → B → C  ✅ (No cycle)
```

### Issue 3: "Model {id} is not running"
**Solution:** 
- Go to Dashboard
- Check model status
- If STOPPED, start it
- If FAILED, redeploy

### Issue 4: "Slow execution"
**Reason:** CPU mode is slow (10-30s per model)
**Solutions:**
- Use smaller models (gpt2, distilgpt2)
- Reduce max_tokens (currently 256)
- Switch to GPU mode for production
- Keep workflows simple (2-3 nodes)

### Issue 5: "Can't connect nodes"
**Solution:**
- Drag from **green dot** (output) to **blue dot** (input)
- Can't connect node to itself
- Can't create duplicate edges

---

## 🎓 Advanced Tips

### Tip 1: Reuse Same Model
You can use the same LLM multiple times with different prompts:
```
GPT-2 (Analyzer) → GPT-2 (Summarizer) → GPT-2 (Formatter)
```

### Tip 2: Validation Node
Add a "validator" node that checks previous outputs:
```
Generator → Validator → Formatter
```

### Tip 3: Multi-Perspective Analysis
Use different models for diverse outputs:
```
Input → GPT-2 (perspective 1)
      → Qwen (perspective 2)
```

### Tip 4: Chain of Thought
Build reasoning chains:
```
Problem → Think → Analyze → Conclude
```

### Tip 5: Prompt Engineering
Test different prompts on the same input:
- Be specific: "Return ONLY positive/negative"
- Add context: "You are an expert analyst"
- Set format: "Reply in one sentence"

---

## 🔬 Technical Details

### Backend Architecture
- **Workflow Engine**: `/backend/app/services/workflow_engine.py`
- **API Router**: `/backend/app/routers/playground.py`
- **Execution**: Topological sort + async execution
- **Model Manager**: Uses `LightweightModelManager`

### Frontend Architecture
- **Canvas**: React Flow library
- **Page**: `/frontend/src/pages/Playground.tsx`
- **Custom Node**: `/frontend/src/components/playground/ModelNode.tsx`
- **State**: React hooks (useState, useCallback)

### API Endpoints
```
GET  /api/playground/available-models  - List running models
POST /api/playground/execute           - Execute workflow
POST /api/playground/validate          - Validate workflow
```

---

## 🎯 Use Cases

### 1. Content Generation Pipeline
```
Input → Topic Analyzer → Content Writer → SEO Optimizer
```

### 2. Sentiment Analysis Chain
```
Input → Sentiment Detector → Emotion Classifier → Report Generator
```

### 3. Multi-Model Validation
```
Input → Model A (Generate)
      → Model B (Validate)
      → Model C (Refine)
```

### 4. Parallel Processing
```
         ┌→ Style Analyzer
Input ───┼→ Tone Detector   ───→ Combiner
         └→ Topic Extractor
```

### 5. Research Assistant
```
Query → Search → Summarize → Cite Sources → Format
```

---

## 🚀 Performance Tips

### For Fast Execution:
1. Use smaller models (GPT-2, DistilGPT-2)
2. Keep workflows under 5 nodes
3. Use parallel structures when possible
4. Test prompts with single nodes first
5. Consider GPU mode for production

### For Best Quality:
1. Use larger models (Qwen2)
2. Chain multiple refinement steps
3. Add validation nodes
4. Use specific, detailed prompts
5. Test with various inputs

---

## 🎉 Ready to Build!

The Playground is **live now**! Go to the Playground tab and start building your first multi-agent workflow!

**Quick Start:**
1. Deploy 2 models
2. Go to Playground
3. Add both models to canvas
4. Connect them: Model 1 → Model 2
5. Edit prompts
6. Run with test input
7. See results!

**Have fun creating amazing LLM pipelines!** 🚀
