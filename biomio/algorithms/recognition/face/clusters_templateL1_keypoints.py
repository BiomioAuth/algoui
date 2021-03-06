from biomio.algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from biomio.algorithms.cvtools import listToNumpy_ndarray, numpy_ndarrayToList
from biomio.algorithms.features import matcherForDetector, dtypeForDetector
from biomio.algorithms.recognition.keypoints import verifying
from biomio.algorithms.features.matchers import Matcher
from biomio.algorithms.logger import logger
import itertools
import numpy


class ClustersTemplateL1MatchingDetector(ClustersMatchingDetector):
    def __init__(self):
        ClustersMatchingDetector.__init__(self)

    def update_hash(self, data):
        del data['keypoints']
        del data['descriptors']
        self._database.append(data)
        self.update_hash_templateL1(data)

    def update_hash_templateL1(self, data):
        """

        max_weight = se*sum(i=1,k-1: 1+2*i) + k*(n-k)*se,
        where
            n - count of images,
            k - count of identical matches, k <= n,
            se - single estimate, I used se=1

        :param data:
        :return:
        """
        knn = 5

        if len(self._database) == 1:
            self._etalon = [[] if cluster is None else [(desc, 1) for desc in cluster]
                            for cluster in data['clusters']]
        else:
            matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))

            for index, et_cluster in enumerate(self._etalon):
                dt_cluster = data['clusters'][index]
                if dt_cluster is None or len(dt_cluster) == 0 or len(dt_cluster) < knn:
                    continue

                for obj in self._database:
                    if data['path'] == obj['path']:
                        continue

                    ob_cluster = obj['clusters'][index]
                    if ob_cluster is None or len(ob_cluster) == 0 or len(ob_cluster) < knn:
                        continue

                    dtype = dtypeForDetector(self.kodsettings.detector_type)
                    matches1 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, dtype),
                                                listToNumpy_ndarray(ob_cluster, dtype), k=knn)

                    for v in matches1:
                        if len(v) >= 1:

                            if v[0].distance == 0:
                                best = v[0]
                            else:
                                best = max(v, key=(lambda m:
                                                   next((c / (1.0 * m.distance) for (d, c) in et_cluster
                                                         if numpy.array_equal(d, ob_cluster[m.trainIdx])), -1
                                                        )
                                                   )
                                           )

                            # et_cluster_ob = [(d, c + 1) for (d, c) in et_cluster
                            #                  if numpy.array_equal(d, ob_cluster[best.trainIdx])]
                            #
                            # if len(et_cluster_ob) == 0:
                            #     et_cluster_ob.append((ob_cluster[best.trainIdx], 1))
                            #
                            # et_cluster_dt = [(d, c + 1) for (d, c) in et_cluster
                            #                  if numpy.array_equal(d, dt_cluster[best.queryIdx])]
                            #
                            # if len(et_cluster_dt) == 0:
                            #     et_cluster_dt.append((dt_cluster[best.queryIdx], 1))
                            #
                            # et_cluster_res = et_cluster_ob + et_cluster_dt
                            # logger.debug("new")
                            # logger.debug(et_cluster_ob)
                            # logger.debug(et_cluster_dt)

                            ob_is = False
                            dt_is = False
                            new_cluster = []
                            for d, c in et_cluster:
                                if numpy.array_equal(d, ob_cluster[best.trainIdx]):
                                    c += 1
                                    ob_is = True
                                if numpy.array_equal(d, dt_cluster[best.queryIdx]):
                                    c += 1
                                    dt_is = True
                                new_cluster.append((d, c))
                            if not ob_is:
                                new_cluster.append((ob_cluster[best.trainIdx], 1))
                            if not dt_is:
                                new_cluster.append((dt_cluster[best.queryIdx], 1))
                            et_cluster = new_cluster
                    self._etalon[index] = et_cluster

    def importSources(self, source):
        self._etalon = []
        logger.debug("Database loading started...")
        self.importSources_L1Template(source.get('data', dict()))
        self._prob = source.get('threshold', 100)
        logger.debug("Database loading finished.")

    def importSources_L1Template(self, source):

        def _values(d, key=None):
            l = sorted(d, key=key)
            for e in l:
                yield d[e]

        self._etalon = [
            [
                (listToNumpy_ndarray(desc_dict['descriptor']), int(desc_dict['count']))
                for desc_dict in _values(cluster, key=int)
            ] for cluster in _values(source, key=int)
        ]

    def exportSources(self):
        data = self.exportSources_L1Template()
        if len(data.keys()) > 0:
            return {
                'data': data,
                'threshold': self._prob
            }
        else:
            return {}

    def exportSources_L1Template(self):
        return {
            str(index): {
                str(i): {
                    'descriptor': numpy_ndarrayToList(d),
                    'count': c
                } for (i, (d, c)) in enumerate(et_weight_cluster)
            } for (index, et_weight_cluster) in enumerate(self._etalon)
        }

    @verifying
    def verify(self, data):
        return self.verify_template_L1(data)

    def verify_template_L1(self, data):
        knn = 2
        matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))
        count = 0
        prob = 0
        logger.debug("Image: " + data['path'])
        logger.debug("Template size: ")
        for index, et_weight_cluster in enumerate(self._etalon):
            d, c = itertools.izip(*itertools.ifilter(lambda (_, c): c > 0, et_weight_cluster))
            et_cluster = list(d)
            cluster_weight = sum(c)
            dt_cluster = data['clusters'][index]

            if et_cluster is None or dt_cluster is None or len(et_cluster) < knn or len(dt_cluster) < knn:
                continue

            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                dtype = dtypeForDetector(self.kodsettings.detector_type)
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster, dtype),
                                            listToNumpy_ndarray(dt_cluster, dtype), k=2)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, dtype),
                                            listToNumpy_ndarray(et_cluster, dtype), k=2)

                ms = [et_cluster[x.queryIdx] for x in itertools.ifilter(
                        lambda (m, n): m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx, itertools.product(
                            itertools.chain(*matches1), itertools.chain(*matches2)
                        )
                )]
                c_val = sum(
                    lambda (_, x): x[1], itertools.ifilter(
                        lambda (m, n): numpy.array_equal(m, n[0]), itertools.product(
                            iter(ms), iter(et_weight_cluster)
                        )
                    )
                )
                count += 1
                val = (c_val / (1.0 * cluster_weight)) * 100
                logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight)
                             + " Positive: " + str(c_val) + " Probability: " + str(val))
                prob += val
            else:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight) + " Invalid.")
        logger.debug("Probability: " + str((prob / (1.0 * count))))
        return prob / (1.0 * count)
