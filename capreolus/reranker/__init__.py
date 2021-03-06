import os
import pickle

from capreolus.registry import ModuleBase, RegisterableModule, Dependency


class Reranker(ModuleBase, metaclass=RegisterableModule):
    """the module base class"""

    module_type = "reranker"
    dependencies = {
        "extractor": Dependency(module="extractor", name="embedtext"),
        "trainer": Dependency(module="trainer", name="pytorch"),
    }

    def save_weights(self, weights_fn, optimizer):
        if not os.path.exists(os.path.dirname(weights_fn)):
            os.makedirs(os.path.dirname(weights_fn))

        d = {k: v for k, v in self.model.state_dict().items() if ("embedding.weight" not in k and "_nosave_" not in k)}
        with open(weights_fn, "wb") as outf:
            pickle.dump(d, outf, protocol=-1)

        optimizer_fn = weights_fn.as_posix() + ".optimizer"
        with open(optimizer_fn, "wb") as outf:
            pickle.dump(optimizer.state_dict(), outf, protocol=-1)

    def load_weights(self, weights_fn, optimizer):
        with open(weights_fn, "rb") as f:
            d = pickle.load(f)

        cur_keys = set(k for k in self.model.state_dict().keys() if not ("embedding.weight" in k or "_nosave_" in k))
        missing = cur_keys - set(d.keys())
        if len(missing) > 0:
            raise RuntimeError("loading state_dict with keys that do not match current model: %s" % missing)

        self.model.load_state_dict(d, strict=False)

        optimizer_fn = weights_fn.as_posix() + ".optimizer"
        with open(optimizer_fn, "rb") as f:
            optimizer.load_state_dict(pickle.load(f))
