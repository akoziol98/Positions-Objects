import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import ConnectionPatch
plt.rcParams.update({'font.size': 18})

def make_boxplots_interaction(df_sit, df_non, y_var, toys, colors, toy_images, fig_size, save_name=0):
    outliers_th = 20
    print(f"Removed points greater than {outliers_th}."
          f"\nSitting: c={len(df_sit[df_sit[y_var] >= outliers_th])}, {(len(df_sit[df_sit[y_var] >= outliers_th]) * 100) / len(df_sit):.2f}%,"
          f"\nOther: c={len(df_non[df_non[y_var] >= outliers_th])}, {(len(df_non[df_non[y_var] >= outliers_th]) * 100) / len(df_non):.2f}%")

    df_sit_plot = df_sit[df_sit[y_var] < outliers_th]
    df_non_plot = df_non[df_non[y_var] < outliers_th]

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=fig_size)

    # SITTING
    ax1.set_title('Independent sitting')
    sns.boxplot(
        data=df_sit_plot, x='Affordances', y=y_var, hue='Affordances',
        fliersize=0,
        boxprops=dict(alpha=.5),
        linewidth=1,
        notch=True,
        medianprops={"color": "grey", "linewidth": 2},
        palette=colors,
        hue_order=toys,
        order=toys,
        dodge=False,
        ax=ax1,
    )

    sns.swarmplot(
        data=df_sit_plot, x='Affordances', y=y_var, hue='Affordances',
        size=6,
        palette=colors,
        hue_order=toys,
        order=toys,
        edgecolor='grey',
        linewidth=1,
        ax=ax1
    )

    for label in toys:
        x_pos = toys.index(label)
        counts = df_sit['Affordances'].value_counts()[label]
        ax1.text(x_pos, df_sit[y_var].min() - 1.8, f'c = {counts}', ha='center', va='bottom')

    # NOT SITTING
    ax2.set_title('Other')

    sns.boxplot(
        data=df_non_plot, x='Affordances', y=y_var,
        fliersize=0,
        boxprops=dict(alpha=.5),
        linewidth=1,
        notch=True,
        medianprops={"color": "grey", "linewidth": 2},
        palette=colors,
        hue_order=toys,
        order=toys,
        ax=ax2,
    )

    sns.swarmplot(
        data=df_non_plot, x='Affordances', y=y_var, hue='Affordances',
        size=6,
        palette=colors,
        hue_order=toys,
        order=toys,
        edgecolor='grey',
        linewidth=1,
        ax=ax2
    )

    for label in toys:
        x_pos = toys.index(label)
        counts = df_non['Affordances'].value_counts()[label]
        ax2.text(x_pos, df_non[y_var].min() - 1.8, f'c = {counts}', ha='center', va='bottom')

        # Add image icons below x-axis
        if len(toy_images.keys()) == 2:
            bubbles_img = toy_images['graspable']['bubbles_img']
            dino_img = toy_images['graspable']['dino_img']
            klickity_img = toy_images['stationary']['klickity_img']
            spinner_img = toy_images['stationary']['spinner_img']

            for ax in [ax1, ax2]:
                image_positions = [0.1, 0.26, 0.64, 0.8]  # Adjusted positions
                images = [bubbles_img, dino_img, klickity_img, spinner_img]
                for xpos, img in zip(image_positions, images):
                    newax = plt.gca().inset_axes([xpos, -0.17, 0.1, 0.1], transform=ax.transAxes)
                    newax.imshow(img)
                    newax.axis('off')

    # Add significance lines
    for xyA, xyB in [
                     #[(0, 20.5), (1, 20.5)],
                     [(0, 19), (0, 19)],
                     [(1, 16), (1, 16)],
                     #[(1, 14.5), (0, 14.5)],
                     ]:
        con = ConnectionPatch(xyA=xyA, coordsA=ax1.transData,
                              xyB=xyB, coordsB=ax2.transData,
                              color='black')


        fig.add_artist(con)

    ax1.text(0.5, 17.5, '***', ha='center', va='bottom')
    ax2.text(0.5, 17.5, '***', ha='center', va='bottom')
    ax2.text(0, 16, 'ns', ha='center', va='bottom')

    ax1.axhline(y=17.5, xmin=0.25, xmax=0.75, color='black', linewidth=1)
    ax2.axhline(y=17.5, xmin=0.25, xmax=0.75, color='black', linewidth=1)

    ax1.axvline(x=0, ymin=0.845, ymax=0.875, color='black', linewidth=1)
    ax1.axvline(x=1, ymin=0.845, ymax=0.875, color='black', linewidth=1)
    ax2.axvline(x=0, ymin=0.845, ymax=0.875, color='black', linewidth=1)
    ax2.axvline(x=1, ymin=0.845, ymax=0.875, color='black', linewidth=1)

    ax1.axvline(x=1, ymin=0.77, ymax=0.80, color='black', linewidth=1)
    ax2.axvline(x=1, ymin=0.77, ymax=0.80, color='black', linewidth=1)

    ax1.axvline(x=0, ymin=0.92, ymax=0.95, color='black', linewidth=1)
    ax2.axvline(x=0, ymin=0.92, ymax=0.95, color='black', linewidth=1)

    ax1.text(1, 19, '***', ha='center', va='bottom')
    # plt.annotate("***", [0.5, 20.5], ha='center', va='bottom')
    # plt.annotate("***", [0.5, 14.5], ha='center', va='bottom')

    for ax in [ax1, ax2]:
        ax.set_facecolor("white")
        ax.set_ylabel('')
        ax.set_xlabel('')
    plt.ylim([0, 20])
    ax1.set_yticklabels([str(int(ytick)) if ytick % 5 == 0 else ytick for ytick in ax1.get_yticks()[:]])
    ax1.set_ylabel('Duration of a manual sampling episode [s]', fontsize=22)
    sns.despine(trim=True)
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.get_yaxis().set_visible(False)
    #
    plt.tight_layout()
    plt.xlabel('')
    plt.subplots_adjust(wspace=0.05)


    if save_name:
        plt.savefig(f"{save_name}", dpi=900)
        print("Plot saved successfully")

    plt.show()

def make_boxplots_interaction_count(df_sit, df_non, y_var, toys, colors, toy_images, fig_size, save_name=0):
    df_sit_plot = df_sit.copy()
    df_non_plot = df_non.copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=fig_size)

    # SITTING
    ax1.set_title('Independent sitting')

    sns.boxplot(
        data=df_sit_plot, x='Affordances', y=y_var, hue='Affordances',
        fliersize=0,
        boxprops=dict(alpha=.5),
        linewidth=1,
        notch=True,
        medianprops={"color": "grey", "linewidth": 2},
        palette=colors,
        hue_order=toys,
        order=toys,
        dodge=False,
        ax=ax1,
    )

    sns.swarmplot(
        data=df_sit_plot, x='Affordances', y=y_var, hue='Affordances',
        size=6,
        palette=colors,
        hue_order=toys,
        order=toys,
        edgecolor='grey',
        linewidth=1,
        ax=ax1
    )
    for label in toys:
        x_pos = toys.index(label)
        counts = df_sit['Affordances'].value_counts()[label]
        ax1.text(x_pos, df_sit[y_var].min() - 1.5, f'n = {counts}', ha='center', va='bottom')

    # NOT SITTING
    ax2.set_title('Other')

    sns.boxplot(
        data=df_non_plot, x='Affordances', y=y_var,
        fliersize=0,
        boxprops=dict(alpha=.5),
        linewidth=1,
        notch=True,
        medianprops={"color": "grey", "linewidth": 2},
        palette=colors,
        hue_order=toys,
        order=toys,
        ax=ax2,
    )

    sns.swarmplot(
        data=df_non_plot, x='Affordances', y=y_var, hue='Affordances',
        size=6,
        palette=colors,
        hue_order=toys,
        order=toys,
        edgecolor='grey',
        linewidth=1,
        ax=ax2
    )
    for label in toys:
        x_pos = toys.index(label)
        counts = df_non['Affordances'].value_counts()[label]
        ax2.text(x_pos, df_non[y_var].min() - 1.5, f'n = {counts}', ha='center', va='bottom')

    #Add image icons below x-axis
    if len(toy_images.keys()) == 2:
        bubbles_img = toy_images['graspable']['bubbles_img']
        dino_img = toy_images['graspable']['dino_img']
        klickity_img = toy_images['stationary']['klickity_img']
        spinner_img = toy_images['stationary']['spinner_img']

        for ax in [ax1, ax2]:
            image_positions = [0.1, 0.26, 0.64, 0.8]  # Adjusted positions
            images = [bubbles_img, dino_img, klickity_img, spinner_img]
            for xpos, img in zip(image_positions, images):
                newax = plt.gca().inset_axes([xpos, -0.14, 0.1, 0.1],transform=ax.transAxes)
                newax.imshow(img)
                newax.axis('off')

    # Add significance lines
    for xyA, xyB in [[(0.5, 31.2), (0.5, 31.2)],
                     [(0.5, 26.1), (0.5, 26.1)],
                     ]:

        con = ConnectionPatch(xyA=xyA, coordsA=ax1.transData,
                              xyB=xyB, coordsB=ax2.transData,
                              color='black')
        fig.add_artist(con)

    ax1.axhline(y=30, xmin=0.25, xmax=0.75, color='black', linewidth=1)

    ax1.axvline(x=0.5, ymin=0.86, ymax=0.89, color='black', linewidth=1)
    ax1.axvline(x=0, ymin=0.82, ymax=0.855, color='black', linewidth=1)
    ax1.axvline(x=1, ymin=0.82, ymax=0.855, color='black', linewidth=1)

    ax2.axhline(y=30, xmin=0.25, xmax=0.75, color='black', linewidth=1)

    ax2.axvline(x=0.5, ymin=0.86, ymax=0.89, color='black', linewidth=1)
    ax2.axvline(x=0, ymin=0.83, ymax=0.855, color='black', linewidth=1)
    ax2.axvline(x=1, ymin=0.83, ymax=0.855, color='black', linewidth=1)

    ax1.axvline(x=0.5, ymin=0.72, ymax=0.75, color='black', linewidth=1)
    ax2.axvline(x=0.5, ymin=0.72, ymax=0.75, color='black', linewidth=1)

    plt.annotate("**", [-0.5, 31.2],  ha='center', va='bottom')
    plt.annotate("***", [-0.5, 26.1], ha='center', va='bottom')

    for ax in [ax1, ax2]:
        ax.set_facecolor("white")
        ax.set_ylabel('')
        ax.set_xlabel('')

    ax1.set_yticklabels([str(int(ytick)) if ytick % 5 == 0 else ytick for ytick in ax1.get_yticks()[1:]])
    ax1.set_ylabel('Frequency of the manual sampling across infants [count/min]', fontsize=22)
    sns.despine(trim=True)
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.get_yaxis().set_visible(False)
    plt.tight_layout()
    plt.xlabel('')
    line = plt.Line2D((0,0), (0,0), color="w", linewidth=3)
    fig.add_artist(line)
    plt.subplots_adjust(wspace=0.05)

    if save_name:
        plt.savefig(f"{save_name}", dpi=900)
        print("Plot saved successfully")

    plt.show()
    plt.close()
