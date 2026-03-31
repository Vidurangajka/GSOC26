import matplotlib.pyplot as plt
import matplotlib.patches as patches

class DRCVisualizer:
    def __init__(self, all_shapes, violations):
        self.all_shapes = all_shapes
        self.violations = violations

    def plot_and_save(self, filename="drc_results.png"):
        print(f"Drawing layout with {len(self.all_shapes)} shapes...")
        
        fig, ax = plt.subplots(figsize=(10, 8))

        # 1. Plot all legal layout shapes
        for shape in self.all_shapes:
            rect_patch = patches.Rectangle(
                (shape.x_min, shape.y_min),
                shape.width(),
                shape.height(),
                linewidth=1,
                edgecolor='#1f77b4',  # Standard blue
                facecolor='#aec7e8',  # Light blue fill
                alpha=0.6
            )
            ax.add_patch(rect_patch)

        # 2. Highlight the violations
        for viol in self.violations:
            for bad_shape in viol['shapes']:
                err_patch = patches.Rectangle(
                    (bad_shape.x_min, bad_shape.y_min),
                    bad_shape.width(),
                    bad_shape.height(),
                    linewidth=2,
                    edgecolor='red',
                    facecolor='none',
                    hatch='////', # Red diagonal warning stripes!
                    zorder=10     # Ensure errors are drawn on top
                )
                ax.add_patch(err_patch)

        # 3. Format the viewport
        ax.autoscale_view()
        plt.axis('equal') # Keep the aspect ratio 1:1 so shapes aren't stretched
        plt.title(f"DRC Agent Verification - {len(self.violations)} Violations Found")
        plt.xlabel("Micrometers (um)")
        plt.ylabel("Micrometers (um)")
        plt.grid(True, linestyle=':', alpha=0.6)
        # Add a text box with the Agent's top 3 fixes
        if self.violations:
            fix_text = "🤖 Agent Fix Suggestions:\n" + "\n".join([v['fix'] for v in self.violations[:3]])
            plt.gcf().text(0.15, 0.02, fix_text, fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
        # 4. Save the file
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {filename}")