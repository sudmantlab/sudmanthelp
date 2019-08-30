
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np

class SeabornFig2Grid():

    def __init__(self, seaborngrid, fig,  subplot_spec):
        self.fig = fig
        self.sg = seaborngrid
        self.subplot = subplot_spec
        if isinstance(self.sg, sns.axisgrid.FacetGrid) or \
            isinstance(self.sg, sns.axisgrid.PairGrid):
            self._movegrid()
        elif isinstance(self.sg, sns.axisgrid.JointGrid):
            self._movejointgrid()
        self._finalize()

    def _movegrid(self):
        """ Move PairGrid or Facetgrid """
        self._resize()
        n = self.sg.axes.shape[0]
        m = self.sg.axes.shape[1]
        self.subgrid = gridspec.GridSpecFromSubplotSpec(n,m, subplot_spec=self.subplot)
        for i in range(n):
            for j in range(m):
                self._moveaxes(self.sg.axes[i,j], self.subgrid[i,j])

    def _movejointgrid(self):
        """ Move Jointgrid """
        h= self.sg.ax_joint.get_position().height
        h2= self.sg.ax_marg_x.get_position().height
        r = int(np.round(h/h2))
        self._resize()
        self.subgrid = gridspec.GridSpecFromSubplotSpec(r+1,r+1, subplot_spec=self.subplot)

        self._moveaxes(self.sg.ax_joint, self.subgrid[1:, :-1])
        self._moveaxes(self.sg.ax_marg_x, self.subgrid[0, :-1])
        self._moveaxes(self.sg.ax_marg_y, self.subgrid[1:, -1])

    def _moveaxes(self, ax, gs):
        #https://stackoverflow.com/a/46906599/4124317
        ax.remove()
        ax.figure=self.fig
        self.fig.axes.append(ax)
        self.fig.add_axes(ax)
        ax._subplotspec = gs
        ax.set_position(gs.get_position(self.fig))
        ax.set_subplotspec(gs)

    def _finalize(self):
        plt.close(self.sg.fig)
        self.fig.canvas.mpl_connect("resize_event", self._resize)
        self.fig.canvas.draw()

    def _resize(self, evt=None):
        self.sg.fig.set_size_inches(self.fig.get_size_inches())


def volcano_plot(data, pvalues, annotation=None, order=None, xlabel="mean", ylabel="-log(adj. pvalue)", title="volcano plot", multitest="fdr_bh", alpha=0.01, keep_xstd=2, keep_ycutoff=10):
    import numpy as np
    from matplotlib import pyplot as plt
    from statsmodels.stats.multitest import multipletests
    from adjustText import adjust_text
    import matplotlib.gridspec as gridspec
    import seaborn as sns

    # remove nan values
    notnan_array = np.logical_not(np.logical_or(np.isnan(data), np.isnan(pvalues)))
    data = data[notnan_array]
    pvalues = pvalues[notnan_array]
    if annotation is not None:
        annotation = annotation[notnan_array]

    # remove extreme x_values
    mean_data = np.mean(data)
    std_data = np.std(data)
    data[data-mean_data>std_data*keep_xstd] = mean_data + std_data*keep_xstd
    data[data-mean_data<-std_data*keep_xstd] = mean_data - std_data*keep_xstd

    if len(pvalues) == 0:
        show_names = []
        adjpvalues = []
    else:
        show_names, adjpvalues, _, _ = multipletests(pvalues, method=multitest, alpha=alpha)

    neglog_adjpvalues = -np.log10(adjpvalues)
    neglog_adjpvalues[neglog_adjpvalues>keep_ycutoff] = keep_ycutoff

    g = sns.jointplot(x=data, y=neglog_adjpvalues, color='k', marginal_kws=dict(bins=15, rug=True), height=8)
    g.ax_joint.hlines(-np.log10(alpha), min(data), max(data), linestyles='dashed')
    g.ax_joint.vlines(0, 0, keep_ycutoff, linestyles='solid')

    if annotation is not None:
        plt_texts = []
        for i, (to_show, x, y, text) in enumerate(zip(show_names, data, neglog_adjpvalues, annotation)):
            if to_show:
                if order is None:
                    plt_texts.append(g.ax_joint.text(x, y, str(i), fontsize=12))
                else:
                    plt_texts.append(g.ax_joint.text(x, y, str(order.loc[text, "Index"]), fontsize=12))
        adjust_text(plt_texts, ax=g.ax_joint)
    g.ax_joint.set_title(title)
    g.ax_joint.set_xlabel(xlabel)
    g.ax_joint.set_ylabel(ylabel)
    g.ax_joint.set_xlim([min(data) - 0.1*(max(data)-min(data)), max(data) + 0.1*(max(data)-min(data))])
    g.ax_joint.set_ylim([0, keep_ycutoff*1.1])
    fig = g.fig

    if order is None:
        g.fig.set_size_inches((13, 8))
        g.ax_joint.set_position([0.1, 0.1, 0.4, 0.6])
        g.ax_marg_x.set_position([0.1, 0.75, 0.4, 0.15])
        g.ax_marg_y.set_position([0.55, 0.1, 0.1, 0.6])

        ax = fig.add_subplot(122)
        ax.set_position([0.7, 0.1, 0.3, 0.8])
        plt.axis('off')
        ax.set_xlim([0, 1])
        if annotation is not None:
            xoffset = 0
            for itext in range(0, len(annotation), 25):
                endtext = itext+25
                if endtext > len(annotation) + 1:
                    endtext = len(annotation) + 1
                ax.text(xoffset, 0, "\n".join([str(i+itext)+": "+note for i, note in enumerate(annotation[itext:endtext])]), fontsize=8)
                xoffset += 25/len(annotation)
        else:
            ax.text(0, 0.5, "There is no annotation for this volcano plot.")
    # fig = plt.figure(figsize=(13,8))
    # gs = gridspec.GridSpec(1, 2)

    # mg0 = SeabornFig2Grid(g, fig, gs[0])
    # mg1 = SeabornFig2Grid(ax, fig, gs[1])

    # gs.tight_layout(fig)

    # put the nan back to adjpvalues
    all_adjpvalues = np.ones(notnan_array.shape) * float("nan")
    all_adjpvalues[notnan_array] = adjpvalues

    return fig, all_adjpvalues
