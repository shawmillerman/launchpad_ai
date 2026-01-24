# Step Chef - AI Cooking Assistant

**Status**: Concept Phase ✅ **Fully Documented**  
**Repository**: `/Users/admin/stepchef` (uses Launchpad AI)  
**Timeline**: 1-2 weeks after Launchpad AI Phase 3

---

## What's New in This Document

This version captures all ideas from your conversations, including:
- ✅ **Flavor Engineering** ("Baller Chef" teaching sear → bloom → deglaze)
- ✅ **Multi-Step UI** (current/previous/next step view, tablet-optimized)
- ✅ **Q&A at Each Step** (ask questions without losing place)
- ✅ **Strategic Time Optimization** ("Save time with AI" through smart prep timing)
- ✅ **Inspirational Tone** (celebrate techniques, positive reinforcement)
- ✅ **Image/OCR Support** (photo upload for recipes, open-source Tesseract)
- ✅ **Calibration Learning** (remember user preferences, track success)

---

## Vision

Step Chef is an AI cooking assistant that transforms how people cook by:
- Reformulating recipes for maximum flavor
- Providing interactive step-by-step guidance
- Adapting to dietary needs and skill levels
- Learning your preferences over time

**Powered by Launchpad AI** - demonstrates the engine's capabilities in a consumer-friendly application.

**Lean dependency**: Uses only the minimal Launchpad AI subset (PDF/TXT + OCR ingestion, single-provider OpenAI embeddings, minimal FAISS retrieval, basic config/logging). Calibration and multi-provider abstractions are deferred until after MVP.

---

## Core Features

### 1. Recipe Intelligence
- **Upload a recipe** (photo, PDF, or text)
- **Analyze the recipe** (brief educational summary)
- **Extract ingredients and steps** using OCR + text processing
- **Teach recipe reading** (how to evaluate recipes, what makes a good recipe)
- **Reformulate for flavor** (umami, spicy, herbaceous profiles)
- **Adapt for dietary needs** (vegan, gluten-free, low-carb)
- **Simplify or elevate** (beginner-friendly vs gourmet techniques)

### 2. Interactive Cooking
- **Step-by-step guidance** with persistent UI showing current, previous, and next steps
- **Q&A at each step**: Ask questions about technique, substitutions, timing
- **Advance button** for manual progression (don't wait for AI timer)
- **Multi-step progression view** (especially tablet/landscape mode with more screen space)
- **Real-time alerts** ("Your pasta will be done in 2 minutes!")
- **Progress tracking** (which step you're on, time remaining, visual progress bar)

### 3. Learning & Personalization
- **Learn from your cooking** (calibration examples)
- **Suggest substitutions** based on your pantry
- **Remember preferences** (e.g., "you like extra garlic")
- **Difficulty adaptation** (recipes get simpler or more complex based on your skill)

---

## Example Workflow

1. **Upload Recipe**
   - Take photo of recipe card, PDF, or paste text
   - Step Chef extracts: "Spaghetti Carbonara, 4 servings"
   - **Brief Recipe Analysis** (new step):
     - Evaluates the recipe structure
     - Identifies improvement opportunities
     - Teaches how to read the recipe better
     - Explains what techniques you'll learn
     - Sets expectations for what's about to happen

2. **Recipe Analysis Summary** (Educational Overview)
   - "This recipe is missing a key technique: building fond for sauce"
   - "You'll learn: Why searing matters, how to bloom spices, sauce building"
   - "Improvements we can make: Add searing step (5 min), bloom spices in fat"
   - "What's next: You'll upload this recipe, we'll enhance it, then cook interactively"
   - **Teaching moment**: "A well-written recipe tells you not just what to do, but why"

3. **Reformulate**
   - "Make it spicier" → Adds chili flakes, adjusts seasoning
   - "Make it vegetarian" → Swaps bacon for mushrooms + smoked paprika
   - "Teach me the classic way" → Shows traditional technique with reasons

4. **Cook Interactively** (Multi-Step UI with Q&A)
   - **Main view shows**: Current step + Previous step (context) + Next step (preview)
   - "Sear beef cubes until brown" → Timer starts
   - Alert: "Your steak is 30 seconds from done—flip now!"
   - **Q&A at each step**: "Can I use turkey bacon?" → "Yes, but reduce cooking by 1 min"
   - **Tablet view**: Uses full screen for current + adjacent steps
   - **Phone view**: Swipeable card for current step with peek at next
   - **Positive reinforcement**: After deglazing, "I know you're a baller chef, because deglazing is what baller chefs do."

4. **Learn Over Time**
   - You rate the recipe 5 stars
   - Step Chef remembers: "User likes spicy Italian, values flavor over speed"
   - Future recipes: More chili, garlic, umami suggestions, and flavor-engineering techniques
   - Tracks your success rate on different techniques (e.g., "You nail deglazing—let's try more pan sauces")

---

## Key Strategic Features

### UI/UX: Multi-Step View with Q&A
- **Current step** is primary focus (large, clear instructions)
- **Previous step** shown above (context: where you came from)
- **Next step** shown below (preview: what's coming)
- **Persistent Q&A**: Ask questions at any step without losing your place
- **Manual advance button**: Don't wait for timers—move to next step when ready
- **Tablet optimization**: Full screen shows all three steps simultaneously with larger type
- **Phone optimization**: Swipeable cards, main step large, adjacent steps as peek
- **Positive tone**: Celebrates techniques as you complete them

**Example After Deglazing**:
```
Previous: ✓ Seared beef cubes until brown
Current:  NOW - Deglaze pan with beef stock, scrape fond
Next:     Return beef to pan and add to crockpot

[Q&A Button] [Next Step]
Message: "I know you're a baller chef, because deglazing is what baller chefs do."
```

### Flavor Engineering: Teach Real Technique
**Not just recipe substitutions—actual flavor education:**
- Recommend searing meat before slow-cooking (Maillard reaction builds depth)
- Bloom spices in hot fat (releases volatile oils, 10x flavor impact)
- Deglaze pans to capture fond (foundational pan sauce technique)
- Build flavor layers (umami, acid balance, heat progression)
- Caramelize vegetables (develop sweetness and complexity)
- Finish with fresh elements (brightness, texture, life)

**Example: Beef Stew Recipe Transformation**
```
Basic Recipe: "Put beef, onions, spices in crockpot"

Step Chef Enhancement:
1. [5 min] Sear beef cubes on high heat until brown
   Why: Maillard reaction creates depth and complexity
   
2. [8 min] Remove beef, cook onions in same pot (beef fat)
   Why: Onions caramelize in rendered fat for sweetness
   
3. [1 min] Bloom spices in hot fat
   Why: Heat releases volatile oils—makes spices 10x more flavorful
   
4. [2 min] Deglaze pan with beef stock, scrape fond
   Why: You're capturing all that browned flavor (fond) into sauce
   
5. [8 hrs] Add beef back + remaining stock to crockpot, cook low
   
Result: Exponentially more complex, developed flavor
```

### Time Optimization: "Save Time with AI"
**Don't just follow recipes—optimize them:**
- **Smart prep timing**: Calculate what to prep when, not just in advance
- **Parallel prep**: While rice cooks, prep vegetables
- **Cooking window usage**: Use downtime strategically
- **Real-time alerts**: "Steak will be done in 30 seconds—prep your plate"
- **Multi-timer coordination**: Track multiple pots/timings
- **Technique shortcuts**: "5-minute sear achieves same flavor goal as 30-minute simmer"

**Example: Chicken Stir-Fry Optimization**
```
❌ Standard Approach: Prep everything (15 min) → Cook (10 min) = 25 min total

✅ Step Chef Approach:
   Step 1: [2 min] Start rice + water boiling
   Step 2: [3 min] Prep hard veggies while rice boils
   Step 3: [3 min] Rice now cooking → prep soft veggies
   Step 4: [1 min] Start wok heating
   Step 5: [8 min] Cook stir-fry (all prep done by now)
   
Result: Same result, 10 min faster (15 min total), better flavor (less oxidation)
```

### Inspirational Tone: Celebrate Learning
- **Celebrate technique mastery**: "Deglazing like a pro!"
- **Teach the why**: "That sear is creating Maillard—you're building flavor."
- **Positive framing**: "You've crushed 15 recipes—ready to try something advanced?"
- **Encourage exploration**: "You nail pan searing—let's try a pan sauce next."
- **Celebrate small wins**: "Perfect fond scrape. That's baller chef stuff."
- **Make learning fun**: "This is where the magic happens."

**Signature Moments**:
```
After deglazing: "I know you're a baller chef, because deglazing is what baller chefs do."
After searing: "Perfect Maillard crust. You're building flavor on a molecular level."
After first recipe: "You just cooked a real meal. That matters."
Encouraging risky step: "Trust the technique. This is where the magic happens."
```

### Image & OCR Support
- **Photo upload**: Snap picture of recipe card, handwritten note, or cookbook page
- **Text extraction**: Open-source Tesseract (free) or Google Cloud Vision (high accuracy)
- **Handwriting recognition**: Works with grandma's handwritten recipes
- **Structural parsing**: Auto-detects ingredients vs steps
- **Status**: OCR is now mature—not a technical blocker. Tesseract handles 95%+ of printed recipes.

### Multi-Timer Management
**Problem**: Cooking multiple items means multiple timers. Easy to forget which timer is for what.

**Solution**: Named timers with intelligent prompting, voice command support, and visual distinction.

**Smart Timer Prompting**:
- **AI detects timer moments**: Analyzes recipe steps to identify when timers are needed
- **Proactive offers**: "This step needs a 5-minute timer—want me to set it?"
- **Voice-friendly responses**: User says "yes", "no", or "set timer in 2 minutes"
- **Quick accept/reject**: One-tap accept or skip
- **Customization**: "Set it for 3 minutes instead" (natural voice commands)
- **No friction**: Removes manual timer creation—AI handles timing intelligence

**Timer Features**:
- **Named timers**: "Rice boiling", "Sauce reducing", "Meat resting"
- **Visual distinction**: Different colors/icons for each timer type
- **Audio + visual alerts**: Sound + on-screen notification when timer expires
- **Multi-timer view**: See all active timers at once
- **One-tap extend**: "Add 2 more minutes" without recreating timer
- **Hands-free compatible**: Works during cooking when hands are full
- **Simple implementation**: Low overhead, high UX value (MVP-ready)

**Example Flow**:
```
Step 1: "Sear beef cubes on high heat"
AI: "This step needs a 5-minute timer. Should I set it?"
User: "Yes"
→ Timer created: "Searing beef - 5:00"

[3 minutes pass]
Step 2: "Add onions to pan"
AI: "Ready to add onions? You've got 2 minutes left on the sear."
User: "Okay"
→ AI automatically suggests: "The onions will caramelize for about 4 minutes. Timer?"
User: "Yes, but make it 3 minutes"
→ Timer created: "Caramelizing onions - 3:00"

[Both timers visible, different colors]
```

**Why this is brilliant**:
- Removes mental load (AI knows when timers are needed)
- Voice-native (perfect for hands-full cooking)
- Personalized timing (user can adjust based on stove/experience)
- Teaches proper timing (user learns when each step matters)

### AI Troubleshooting & Hands-Free Voice Coaching
**Problem**: When something goes wrong mid-cook (sauce breaks, meat overcooked), user is stuck. And they can't easily ask for help because hands are covered in food.

**Solution**: AI actively monitors cooking, offers hands-free course correction, and voice-guided recovery.

**How It Works**:

**Reactive Mode** (User reports problem):
- User: "Something's wrong with the sauce" or calls the app
- AI: Asks diagnostic questions via voice-only ("Is it too thin or too thick?")
- AI: Suggests recovery ("Add 1 tbsp cornstarch slurry to thicken")
- User follows guidance hands-free

**Proactive Mode** (AI pings for check-ins):
- Every 60 seconds during critical steps: "How's the sear going?"
- AI listens for issues ("It's sticking" / "It looks perfect" / "I'm not sure")
- If problem detected, immediately suggests fix
- Hands never leave the stove

**Voice Features**:
- **Speech-to-text**: User speaks problems naturally ("I think I burned it")
- **Text-to-speech**: AI responds with guidance (no reading required)
- **Voice commands**: "Next step", "Add timer for 5 min", "I need help"
- **Fallback**: Text input always available (but voice is primary during cooking)

**Course Correction Examples**:
- Sauce breaking? → "Add cold butter slowly while whisking off heat"
- Meat overcooked? → "Rest it now, slice thin, sauce heavily"
- Forgot an ingredient? → "Add it now in this order to fix timing"
- Burning smell? → "Move to cooler burner, check your heat"

**Why this is huge**:
- Removes anxiety from cooking (you're never truly stuck)
- Hands-free = realistic for actual cooking (not reading while handling food)
- Teaches problem-solving, not just following steps
- Transforms Step Chef from "recipe bot" to "live coach"

**Implementation notes**:
- Uses Launchpad AI's LLM layer for diagnosis
- Voice I/O via Web Speech API (browser) or Twilio (phone)
- Optional feature (users can disable proactive pings)
- Pings frequency configurable ("Every 30 sec" / "Every 2 min" / "On demand only")
- Phase timeline: Phase 4+ (depends on voice infrastructure)

---

## Technical Architecture

### 1. Flavor Reformulation (The "Baller Chef" Feature)
Not just substitutions—**actual flavor engineering** that teaches proper technique:
- Build flavor through technique, not just ingredients
- Recommend searing meat before slow-cooking (Maillard reaction)
- Bloom spices in fat for depth
- Deglaze pans to capture fond and build sauce
- Optimize ingredient order to maximize flavor extraction
- Balance flavors (e.g., add acid to cut richness, umami to deepen)

**Example: Beef Stew Upgrade**
```
Basic Recipe:
"Put beef roast, onions, and spices in crockpot"

Step Chef Enhancement (Flavor Engineering):
1. Sear beef cubes 8 minutes in hot pot → Maillard browning
2. Remove and set aside
3. Cook onions in beef fat → builds fond
4. BlooStrategic Time Optimization
**Save time with AI**—don't just follow recipes, optimize them:
- **Smart prep timing**: Figure out what to prep when, not just in advance
- **Parallel prep**: Prep ingredient B while ingredient A cooks
- **Downtime optimization**: Use cooking windows strategically
- **Real-time alerts**: "Steak will be done in 30 seconds, flip now"
- **Photo/image upload**: Take picture of recipe card, handwritten note, or printed recipe
- **Text extraction**: Industry-standard OCR (Tesseract open-source, or Google Cloud Vision API)
- **Structural parsing**: Detect ingredients section vs cooking steps
- **Quality validation**: Verify extracted text is actually a recipe
- **Handwriting support**: Works with grandma's handwritten recipe card
- **Note**: OCR is now mature/trivial (open-source Tesseract works well for most use cases; paid APIs offer better accuracy for edge cases). Not a major concern for this project.
**Example: Chicken Stir-Fry**
```
Standard approach: Prep everything (15 min), then cook (10 min)
Step Chef approach:
- Start rice/water (2 min) → while boiling, start prep
- Prep hard veggies (carrots, broccoli stems) - 3 min
- Rice is now cooking → prep soft veggies while waiting
- Start wok heating → by time you finish prep, wok is hot
- Total time savings: ~10 min, better flavor (less oxidation from early prep)
```

Result: Exponentially more complex, developed flavor
Vibe: "I know you're a baller chef, because deglazing is what baller chefs do."
```

**Flavor Engineering Profiles:**
- Umami/Savory: Sear, bloom, deglaze, fond-building
- Bright/Fresh: Fresh herb timing, acid balance, finishing touches
- Herbaceous: Spice blooming, herb layering (hardy herbs early, delicate herbs late)
- Depth/Richness: Caramelization, long cooking, layered technique

### 2. Calibration-Based Personalization
Uses Launchpad AI's calibration engine:
- Store your cooking sessions as calibration examples
- Future recipes use similarity search: "Similar to that pasta you loved"
- Adapt complexity based on your success rate

### 3. Real-Time Cooking Alerts
- Parse timing from recipe steps
- Set multiple timers automatically
- Alert when critical steps approach ("Flip steak in 30 seconds!")

### 4. Visual Recipe Recognition
- OCR for handwritten recipes (grandma's recipe card)
- Structural parsing (detect ingredients vs steps)
- Quality validation (is this a recipe or random text?)

---

## Technical Architecture

### Launchpad AI Components Used

| Component | How Step Chef Uses It |
|-----------|----------------------|
| **Ingestion** | Extract recipes from PDFs, images, text |
| **Quality Gates** | Validate recipe structure (has ingredients? has steps?) |
| **Embeddings** | Find similar recipes for substitution suggestions |
| **Retrieval** | Search your past cooking sessions for preferences |
| **Calibration** | Learn from your ratings and cooking success |
| **Multi-Provider LLMs** | Use Gemini for reformulation, OpenAI for Q&A |

### Step Chef-Specific Code

```
stepchef/
├── app/
│   ├── recipe_parser.py      # Extract ingredients & steps from text
│   ├── reformulator.py       # Flavor profile transformations
│   ├── cooking_session.py    # Interactive cooking guidance
│   ├── timer_manager.py      # Multi-timer coordination
│   └── ui.py                 # CLI or web interface
├── config/
│   ├── flavor_profiles.yaml  # Spicy, umami, herbaceous definitions
│   ├── dietary_rules.yaml    # Vegan, gluten-free substitutions
│   └── skill_levels.yaml     # Beginner vs advanced adaptations
└── data/
    └── recipes/              # Your recipe collection
```

### Data Flow

1. **Input**: User uploads recipe (photo/PDF/text)
2. **Launchpad AI Ingestion**: Extract clean text, quality validation
3. **Recipe Parser**: Identify ingredients vs steps
4. **Reformulation**: Apply flavor profile transformations
5. **Storage**: Save to vector store with embeddings
6. **Cooking Session**: Guide user step-by-step with timers
7. **Calibration**: Capture user rating and preferences

---

## User Stories

### Beginner Cook
*"I'm new to cooking and recipes are confusing."*
- Step Chef simplifies: Fewer steps, more explanations
- Detects when you're stuck: "Need help with this step?"
- Learns your pace: Adjusts timing suggestions

### Home Chef
*"I want to make recipes more flavorful."*
- Step Chef reformulates: "Add fish sauce for umami"
- Suggests techniques: "Try dry-brining overnight"
- Explains why: "Maillard reaction creates complexity"

### Dietary Restrictions
*"I'm vegan but love Italian food."*
- Step Chef adapts: "Use nutritional yeast instead of parmesan"
- Maintains flavor: "Add miso for umami depth"
- Learns preferences: "You prefer cashew cream over soy"

---

## MVP Scope (2 weeks)

### Phase 1: Recipe Ingestion (Week 1)
- [ ] Text-based recipe input (paste or upload .txt)
- [ ] Parse ingredients vs steps
- [ ] Quality validation (has ingredients? has steps?)
- [ ] Store in Launchpad AI vector store

### Phase 2: Basic Reformulation (Week 1)
- [ ] Spicy profile (add chili, adjust seasoning)
- [ ] Simplify mode (reduce steps, add guidance)
- [ ] Ingredient substitution (config-driven)

### Phase 3: Interactive Cooking (Week 2)
- [ ] Step-by-step CLI guidance
- [ ] **Multi-timer support** (MVP-ready feature—named timers with visual distinction)
- [ ] Q&A during cooking (LLM-powered)

### Phase 4: Learning (Week 2)
- [ ] Capture user ratings
- [ ] Store as calibration examples
- [ ] Use similarity search for future suggestions

### Phase 5: Voice & Troubleshooting (Week 3-4, post-MVP)
- [ ] Voice input/output infrastructure
- [ ] Proactive health checks ("How's the sear going?")
- [ ] Reactive troubleshooting (user reports problem, AI suggests fix)
- [ ] Course correction guidance
- [ ] Hands-free voice commands

### Deferred (Post-MVP)
- Image/OCR recipe extraction
- Web UI
- Advanced flavor engineering
- Pantry inventory tracking
- Nutritional analysis

---

## Demo Scenarios

### Demo 1: Spicy Upgrade
```
Input: Classic Marinara Sauce recipe
Command: "Make it spicier"
Output: 
  - Add 1 tsp red chili flakes
  - Include 2 minced jalapeños
  - Add 1/4 tsp cayenne to sauce
  - Garnish with fresh chili slices
```

### Demo 2: Beginner Simplification
```
Input: Complex French Onion Soup (12 steps)
Command: "Simplify for beginners"
Output: Reduced to 6 steps with extra guidance:
  - Step 1: "Slice onions thinly (about 1/4 inch)"
  - Step 2: "Cook onions on medium heat for 20 minutes, stirring every 5 minutes"
  - [Clear, simple instructions]
```

### Demo 3: Dietary Adaptation
```
Input: Spaghetti Carbonara (bacon, eggs, parmesan)
Command: "Make it vegan"
Output:
  - Replace bacon → mushrooms + smoked paprika
  - Replace eggs → silken tofu + nutritional yeast
  - Replace parmesan → cashew parmesan
  - Maintains creamy texture and umami flavor
```

---

## Success Metrics

### User Experience
- **Recipe Clarity**: Users understand 90%+ of steps without confusion
- **Flavor Satisfaction**: 4+ star ratings on 80%+ of reformulated recipes
- **Cooking Success**: Users complete 90%+ of started cooking sessions

### Technical Performance
- **Recipe Parsing Accuracy**: 95%+ correct ingredient/step identification
- **Reformulation Speed**: <2 seconds for flavor profile changes
- **Q&A Response Time**: <3 seconds for cooking questions

### Learning Effectiveness
- **Preference Detection**: System learns user preferences after 5-10 rated recipes
- **Substitution Relevance**: 80%+ of suggestions are rated "helpful"

---

## Competitive Positioning

| Feature | Step Chef | Recipe Apps | ChatGPT |
|---------|-----------|-------------|---------|
| Recipe reformulation | ✅ Flavor-engineered | ❌ Basic substitutions | ✅ Generic suggestions |
| Interactive cooking | ✅ Real-time guidance | ⚠️ Static instructions | ❌ No real-time |
| Multi-timer management | ✅ Named timers | ❌ No timers | ❌ No timers |
| Hands-free voice coaching | ✅ Proactive + reactive | ❌ No voice | ⚠️ Text-only |
| Troubleshooting | ✅ AI course correction | ❌ Fixed recipe | ⚠️ Generic advice |
| Learning preferences | ✅ Calibration-based | ❌ No learning | ❌ No memory |
| Quality validation | ✅ Built-in gates | ❌ Accepts garbage | ⚠️ Sometimes hallucinates |
| Transparent | ✅ Citations & reasoning | ❌ Opaque | ⚠️ Sometimes explains |

---

## Future Enhancements

### Phase 2 (Months 2-3)
- Visual recipe recognition (OCR)
- Multi-timer coordination
- Web UI with photos
- Voice commands ("Alexa, next step")

### Phase 3 (Months 4-6)
- Advanced flavor engineering
- Pantry inventory tracking
- Meal planning
- Shopping list generation
- Nutritional analysis

### Enterprise Features
- Restaurant recipe scaling (4 servings → 100 servings)
- Cost optimization
- Allergen detection and warnings
- Supply chain substitutions

---

## Getting Started (After Launchpad AI is Ready)

```bash
# Clone Step Chef
git clone <stepchef-repo>
cd stepchef

# Install Launchpad AI (as dependency)
pip install -e ../launchpad_ai

# Install Step Chef requirements
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add API keys

# Try a demo recipe
python -m app.cook --recipe examples/carbonara.txt --profile spicy
```

---

## Questions for Future Development

1. **Business Model**: Free tier + Premium ($5/mo for advanced features)?
2. **Data Privacy**: Store recipes locally or cloud sync?
3. **Integration**: Partner with recipe sites (AllRecipes, NYT Cooking)?
4. **Hardware**: Smart kitchen integrations (Instant Pot, smart ovens)?

---

**Step Chef Status**: Concept complete, ready for implementation once Launchpad AI Phase 3 is done.

**Next Steps**:
1. Finish Launchpad AI Phases 1-3
2. Build Step Chef MVP (2 weeks)
3. Test with 10 beta users
4. Iterate based on feedback
