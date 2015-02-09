from algorithms.features.classifiers import CascadeROIDetector
from algorithms.cvtools.visualization import showClusters
from algorithms.features.detectors import (BRISKDetector, ORBDetector,
                                           BRISKDetectorSettings, ORBDetectorSettings)
from algorithms.features.classifiers import getROIImage
from algorithms.recognition.features import (FeatureDetector,
                                             BRISKDetectorType, ORBDetectorType)
from algorithms.features.matchers import FlannMatcher
from algorithms.cvtools.types import listToNumpy_ndarray
from lshash import LSHash
from algorithms.hashing.nearpy_hash import NearPyHash
from algorithms.clustering.forel import FOREL
from algorithms.clustering.kmeans import KMeans
import logger
import os


LSHashType = 0
NearPyHashType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    neighbours_distance = 1.0
    max_hash_length = 600
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()


def identifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Identifying...")
        res = None
        if self.data_detect(self, data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Identifying finished.")
        return res
    return wrapped


def verifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Verifying...")
        res = None
        if self.data_detect(data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Verifying finished.")
        return res
    return wrapped


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self):
        #     self._data_keys = dict()
        self._hash = None
        #     self._data_init = False
        self._cascadeROI = None
        self._detector = None
        self._eyeROI = None
    #
    # def init_hash(self):
    #     self._cascadeROI = CascadeROIDetector()
    #     for cascade in self.kodsettings.cascade_list:
    #         self._cascadeROI.add_cascade(cascade)
    #     self._eyeROI = CascadeROIDetector()
    #     self._eyeROI.classifierSettings.minNeighbors = 1
    #     self._eyeROI.classifierSettings.scaleFactor = 1.2
    #     for cascade in self.kodsettings.clusters_cascade:
    #         self._eyeROI.add_cascade(cascade)
    #     if self.kodsettings.detector_type is BRISKDetectorType:
    #         size = 64
    #     else:
    #         size = 32
    #     if self._hash_type is LSHashType:
    #         self._hash = LSHash(128, size)
    #     else:
    #         if self._data_type is FeaturesMatching:
    #             self._hash = NearPyHash(size)
    #             self._hash.addRandomBinaryProjectionsEngine(10)
    #         elif self._data_type is SpiralKeypointsVector:
    #             self._hash = NearPyHash(self.kodsettings.max_hash_length)
    #             self._hash.addRandomBinaryProjectionsEngine(10)
    #     self._data_init = True
    #
    # def hash_initialized(self):
    #     return self._data_init

    def addSource(self, data):
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        for data in data_list:
            self.addSource(data)

    @identifying
    def identify(self, data):
    #         if self._data_type is FeaturesMatching:
    #             if len(self._data_keys) > 0:
    #                 res = self.matching(data)
    #         elif self._data_type is SpiralKeypointsVector:
    #             res = self.vect_matching(data)
        pass

    @verifying
    def verify(self, data):
    #         if self._data_type is FeaturesMatching:
    #             logger.logger.debug("Data Type doesn't support image verification.")
    #         elif self._data_type is SpiralKeypointsVector:
    #             logger.logger.debug("Data Type doesn't support image verification.")
        pass

    def data_detect(self, data):
        # ROI detection
        rect = self._cascadeROI.detectAndJoin(data['data'])
        # ROI cutting
        data['roi'] = getROIImage(data['data'], rect)
        # Keypoints detection
        detector = FeatureDetector()
        if self.kodsettings.detector_type is BRISKDetectorType:
            brisk_detector = BRISKDetector(self.kodsettings.brisk_settings.thresh,
                                           self.kodsettings.brisk_settings.octaves,
                                           self.kodsettings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            orb_detector = ORBDetector(self.kodsettings.orb_settings.features,
                                       self.kodsettings.orb_settings.scaleFactor,
                                       self.kodsettings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        obj = detector.detectAndComputeImage(data['roi'])
        data['keypoints'] = obj['keypoints']
        data['descriptors'] = obj['descriptors']
        if data['descriptors'] is None:
            data['descriptors'] = []
            # if self._data_type is FeaturesMatching:
            #     key_arrays = keypointsToArrays(obj.keypoints())
            #     data['keypoints'] = key_arrays
            # elif self._data_type is SpiralKeypointsVector:
            #     height, width = data['roi'].shape[0], data['roi'].shape[1]
            #     order_keys = obj.keypoints()  # spiralSort(obj, width, height)
            # order_keys = minimizeSort(obj)
            # obj.keypoints(keypointsToArrays(order_keys))
            # key_arr = joinVectors(obj.keypoints())
            # while len(key_arr) < self.kodsettings.max_hash_length:
            #     key_arr.append(0)
            # data['keypoints'] = listToNumpy_ndarray(key_arr)
        self._detect(data, detector)
        return True

    def _detect(self, data, detector):
        pass

    def update_hash(self, data):
        pass
        #     if self._hash_type is LSHashType:
        #         for keypoint in data['keypoints']:
        #             self._hash.index(keypoint)
        #     else:
        #         if self._data_type is FeaturesMatching:
        #             for keypoint in data['keypoints']:
        # for keypoint in data['descriptors']:
        #     self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])
        #     value = self._data_keys.get(os.path.split(data['path'])[0], 0)
        #     value += 1
        #     self._data_keys[os.path.split(data['path'])[0]] = value
        # elif self._data_type is SpiralKeypointsVector:
        #     self._hash.add_dataset(data['descriptors'], os.path.split(data['path'])[0])

        # def matching(self, data):
        #     imgs = dict()
        #     if data is not None:
        #         for keypoint in data['descriptors']:
        #             neig = self._hash.neighbours(keypoint)
        #             for el in neig:
        #                 if el[2] < self.kodsettings.neighbours_distance:
        #                     value = imgs.get(el[1], 0)
        #                     value += 1
        #                     imgs[el[1]] = value
        #         keys = imgs.keys()
        #         vmax = 0
        #         max_key = ""
        #         for key in keys:
        #             if imgs[key] > vmax:
        #                 max_key = key
        #                 vmax = imgs[key]
        #         logger.logger.debug(imgs)
        #         logger.logger.debug(max_key)
        #         logger.logger.debug(self._data_keys[max_key])
        #         logger.logger.debug(len(data['descriptors']))
        #         logger.logger.debug(imgs[max_key] / (self._data_keys[max_key] * 1.0))
        #         return max_key
        #     return None
        #
        # def vect_matching(self, data):
        #     imgs = dict()
        #     if data is not None:
        #         neig = self._hash.neighbours(data['keypoints'])
        #         logger.logger.debug(neig)
        #         for el in neig:
        #             if el[2] < self.kodsettings.neighbours_distance:
        #                 value = imgs.get(el[1], 0)
        #                 value += 1
        #                 imgs[el[1]] = value
        #         keys = imgs.keys()
        #         vmax = 0
        #         max_key = ""
        #         for key in keys:
        #             if imgs[key] > vmax:
        #                 max_key = key
        #                 vmax = imgs[key]
        #         logger.logger.debug(imgs)
        #         logger.logger.debug(max_key)
        #         return max_key
        #     return None


class ObjectsMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self.etalon = []
        self._hash = []

    def update_hash(self, data):
        del data['data']
        del data['roi']
        del data['keypoints']
        self._hash.append(data)
        ##############################################
        if len(self.etalon) == 0:
            self.etalon = data['descriptors']
        else:
            matcher = FlannMatcher()
            matches1 = matcher.knnMatch(self.etalon, data['descriptors'], k=1)
            matches2 = matcher.knnMatch(data['descriptors'], self.etalon, k=1)

            good = []
            # for v in matches:
            #         if len(v) >= 1:
                    # if len(v) >= 2:
                    #     m = v[0]
                    # n = v[1]
                    # good.append(self.etalon[m.queryIdx])
                    #     if m.distance < self.kodsettings.neighbours_distance:
                    #         good.append(self.etalon[m.queryIdx])
                    # good.append(data['descriptors'][m.queryIdx])
                    # good.append(self.etalon[m.trainIdx])
                    #
                    # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    #     good.append(self.etalon[m.queryIdx])
                    # else:
                    #     good.append(self.etalon[m.queryIdx])
                    #     good.append(data['descriptors'][m.trainIdx])
                    # good.append(data['descriptors'][m.queryIdx])
                    # good.append(self.etalon[m.trainIdx])

            for v in matches1:
                if len(v) >= 1:
                    m = v[0]
                    for c in matches2:
                        if len(c) >= 1:
                            n = c[0]
                            if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                good.append(self.etalon[m.queryIdx])
                                good.append(data['descriptors'][n.queryIdx])
            self.etalon = listToNumpy_ndarray(good)

    @identifying
    def identify(self, data):
        imgs = dict()
        matcher = FlannMatcher()
        for d in self._hash:
            matches = matcher.knnMatch(d['descriptors'],
                                       data['descriptors'],
                                        k=2)
            good = []
            count = len(matches)
            for v in matches:
                if len(v) is 2:
                    m = v[0]
                    n = v[1]
                    if m.distance < self.kodsettings.neighbours_distance * n.distance:
                        good.append([m])
                    else:
                        count -= 1
            key = d['path']
            value = imgs.get(key, dict())
            value['id'] = os.path.split(d['path'])[1]
            value['all'] = count
            value['positive'] = len(good)
            value['negative'] = count - len(good)
            value['prob'] = len(good) / (1.0 * count)
            imgs[key] = value
        res = self.merge_results(imgs)
        result = self.print_dict(res)
        return result

    @verifying
    def verify(self, data):
        matcher = FlannMatcher()
        matches = matcher.knnMatch(self.etalon, data['descriptors'], k=1)
        # matches2 = matcher.knnMatch(data['descriptors'], self.etalon, k=1)
        ms = []
        for v in matches:
            if len(v) >= 1:
            # if len(v) >= 2:
                m = v[0]
                # n = v[1]
                # logger.logger.debug(str(m.distance) + " " + str(m.queryIdx) + " " + str(m.trainIdx) + " | "
                # + str(n.distance) + " " + str(n.queryIdx) + " " + str(n.trainIdx))
                if m.distance < self.kodsettings.neighbours_distance:
                # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    ms.append(m)
                # else:
                #     ms.append(m)
                #     ms.append(n)
            # for v in matches1:
            # if len(v) >= 1:
            #         m = v[0]
            #         for c in matches2:
            #             if len(c) >= 1:
            #                 n = c[0]
            #                 if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
            #                     ms.append(m)

        logger.logger.debug("Image: " + data['path'])
        logger.logger.debug("Template size: " + str(len(self.etalon)) + " descriptors.")
        logger.logger.debug("Positive matched descriptors: " + str(len(ms)))
        logger.logger.debug("Probability: " + str((len(ms) / (1.0 * len(self.etalon))) * 100))
        return True

    @staticmethod
    def merge_results(results):
        mres = dict()
        res = dict()
        for key in results.keys():
            value = results.get(key, dict())
            str_key = os.path.split(key)[0]
            avg = mres.get(str_key, dict({'id': str_key, 'all': 0, 'positive': 0,
                                          'negative': 0, 'prob': 0, 'count': 0}))
            avg['all'] += value['all']
            avg['positive'] += value['positive']
            avg['negative'] += value['negative']
            avg['prob'] += value['prob']
            avg['count'] += 1
            mres[str_key] = avg
            for k in mres.keys():
                value = mres.get(k, dict())
                dic = dict()
                dic['id'] = value['id']
                dic['all'] = value['all']  # / value['count']
                dic['positive'] = value['positive']  # / value['count']
                dic['negative'] = value['negative']  # / value['count']
                dic['prob'] = value['prob'] / value['count']
                res[k] = dic
            return res

    @staticmethod
    def print_dict(d):
        logs = "Keys\tAll Matches\tPositive Matches\tNegative Matches\tProbability\n"
        amatches = 0
        gmatches = 0
        nmatches = 0
        prob = 0
        count = 0
        max_val = 0
        max_key = ''
        max_low = 0
        low_key = ''
        for key in d.keys():
            value = d.get(key, dict())
            logs += (value['id'] + "\t" + str(value['all']) + "\t" + str(value['positive']) + "\t"
                     + str(value['negative']) + "\t" + str(value['prob'] * 100) + "\n")
            amatches += value['all']
            gmatches += value['positive']
            nmatches += value['negative']
            prob += value['prob'] * 100
            count += 1
            if max_val < value['prob']:
                max_key = key
                max_val = value['prob']
            if max_low < value['prob'] and max_key != key:
                low_key = key
                max_low = value['prob']
        v = d.get(max_key, dict())
        logs += ("Max:\t" + v['id'] + "\t" + str(v['all']) + "\t" + str(v['positive']) + "\t"
                 + str(v['negative']) + "\t" + str(v['prob'] * 100) + "\n")
        v1 = d.get(low_key, dict())
        logs += ("Next:\t" + v1['id'] + "\t" + str(v1['all']) + "\t" + str(v1['positive']) + "\t"
                 + str(v1['negative']) + "\t" + str(v1['prob'] * 100) + "\n")
        logs += ("Total:\t\t" + str(amatches) + "\t" + str(gmatches) + "\t" + str(nmatches)
                 + "\t" + str(prob) + "\n")
        if count > 0:
            logs += ("Average:\t\t" + str(amatches / (1.0 * count)) + "\t" + str(gmatches / (1.0 * count))
                     + "\t" + str(nmatches / (1.0 * count)) + "\t" + str(prob / (1.0 * count)) + "\n")
        logger.logger.debug(logs)
        return max_key


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = []

    def update_hash(self, data):
        del data['data']
        del data['roi']
        del data['keypoints']
        del data['descriptors']
        self._hash.append(data)

    @verifying
    def verify(self, data):
        matcher = FlannMatcher()
        gres = []
        for d in self._hash:
            res = []
            logger.logger.debug("Source: " + d['path'])
            for i in range(0, len(d['clusters'])):
                test = data['clusters'][i]
                source = d['clusters'][i]
                matches = matcher.knnMatch(test, source, k=1)

                ms = []
                for v in matches:
                    if len(v) >= 1:
                        # if len(v) >= 2:
                        m = v[0]
                        # n = v[1]
                        if m.distance < self.kodsettings.neighbours_distance:
                            ms.append(m)
                prob = len(ms) / (1.0 * len(matches))
                res.append(prob * 100)
                logger.logger.debug("Part #" + str(i + 1) + ": " + str(prob * 100) + "%")
            suma = 0
            for val in res:
                suma += val
            logger.logger.debug("Total for image: " + str(suma / len(res)))
            gres.append(suma / len(res))
        s = 0
        for val in gres:
            s += val
        logger.logger.debug("Total: " + str(s / len(gres)))
        return True

    def _detect(self, data, detector):
        # ROI detection
        rect = self._eyeROI.detectAndJoin(data['roi'])
        if len(rect) <= 0:
            return False
        # ROI cutting
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        center = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        # out = paintLine(data['roi'], (lefteye[0], lefteye[1], righteye[0], righteye[1]), (255, 0, 0))
        # out = paintLine(out, (lefteye[0], lefteye[1], center[0], center[1]), (255, 0, 0))
        # out = paintLine(out, (righteye[0], righteye[1], center[0], center[1]), (255, 0, 0))
        #     drawImage(out)
        centers = [lefteye, righteye, center]

        clusters = KMeans(data['keypoints'], 0, centers)
        # clusters = FOREL(obj['keypoints'], 40)
        # showClusters(clusters, out)
        descriptors = []
        for cluster in clusters:
            desc = detector.computeImage(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
        data['clusters'] = descriptors