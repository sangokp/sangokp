# Custom Snake Game Integration Package  

This repository contains a custom snake game implemented in `custom_snake_complete.py`. The goal is to replace the default GitHub contribution snake animation with this custom game, which features colored dots that move, shoot projectiles, and are eaten by the snake. The snake's tail length has been extended to six segments.  

## Files  
- `custom_snake_complete.py` – Python script implementing the custom snake game. It defines classes for Dot, Projectile, Snake, and Game. The script currently simulates the game and writes step-by-step logs to `dist/custom_snake_log.txt`.  
- `.github/workflows/snake.yml` – Existing GitHub Actions workflow for generating the default snake animation using the Platane/snk action.  

## Pending Tasks for Integration (for Claude)  
1. **Modify `custom_snake_complete.py` (if needed):**  
   - Ensure the script can generate a GIF or SVG animation instead of just logging to a text file. This might involve using a graphics library such as Pillow or Cairo to render the grid and save frames.  
   - Confirm that the snake starts with six segments and that colored dots move, shoot, and are eaten as specified.  

2. **Create/modify a GitHub Actions workflow:**  
   - Set up a job that installs Python and runs `custom_snake_complete.py` to generate the animation file (e.g., `dist/custom_snake.gif`).  
   - Commit the generated animation to the `output` branch (similar to how the current `snake.yml` publishes `github-snake.svg`).  
   - Adjust the existing workflow or create a new one so that it does not conflict with the default `Platane/snk` action.  

3. **Update the `README.md`:**  
   - Replace the `<picture>` tag that references `github-snake.svg` with an image link to the new custom animation (e.g., `https://raw.githubusercontent.com/<username>/<repo>/output/custom_snake.gif`).  
   - Describe the custom snake game and its features.  

4. **Test the Workflow:**  
   - Run the workflow to ensure that the custom animation is generated and published correctly.  
   - Verify that the README displays the new animation on your GitHub profile.  

## Notes  
- The default `Platane/snk` GitHub Action only allows customization of colors, not game mechanics or snake length. The custom Python script is required for advanced features.  
- The `dist` directory is used for workflow outputs. Ensure it exists before running the script.  
- When developing the animation generation, keep the GitHub contribution grid dimensions in mind (7 rows × 53 columns).  

---  

This document is provided to help the next agent (Claude) understand the current state of the repository and the steps needed to complete integration.
