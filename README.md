# minecraft-py
A custom 3D renderer and basic game engine. Built with customizability and sustainability in mind, with a modular, reusable class structure. Inspired by Minecraft and its voxel-style (although it isn't limited to a fixed grid!)

Key features:
- Modularity-focused, with distinct handlers for blocks, camera rendering, player movement and collisions, on-screen graphics, etc.
  - Makes it easy to change camera views, create new derived blocks, modify rendering pipeline, and more without interfering with other components
- Optimized 3D rendering with culling and clipping, using projection-based perspective rendering
- Simple, expandable block models, allowing for easy manipulation and modification
- Built in support for custom assets makes it possible to import OBJ files directly into the world
- Player physics and entity support for movement, collision, camera perspectives, and entity interactions
- Debug modes to view hitboxes, face normals, entity edges, block properties, etc.
