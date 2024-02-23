import PySpin as spin
import sys


class PointgreyCamera():
    def __init__(self):
        self.cam = None
        self.system = spin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        if self.cam_list.GetSize() == 0:
            print("There is no camera available. \
                  The system will been aborting...")
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            sys.exit(0)
        else:
            for cam in self.cam_list:
                self.cam = cam
                break
        self.cam.Init()
        self.max_exposure_time = self.cam.ExposureTime.GetMax()
        self.min_exposure_time = self.cam.ExposureTime.GetMin()
        self.min_gain = self.cam.Gain.GetMin()
        self.max_gain = self.cam.Gain.GetMax()
        self.min_gamma = self.cam.Gamma.GetMin()
        self.max_gamma = self.cam.Gamma.GetMax()
        self.exposure_time = 100

        try:
            if self.cam.AcquisitionMode.GetAccessMode() != spin.RW:
                print("Acquistion mode cannot be set")
                self.close_camera()
                sys.exit(1)
            else:
                self.cam.AcquisitionMode.SetValue(spin.AcquisitionMode_Continuous)

            self.cam.BeginAcquisition()
            self.processor = spin.ImageProcessor()
            self.processor.SetColorProcessing(spin.HQ_LINEAR)
        except spin.SpinnakerException as ex:
            print(f"Error: {ex}")
            self.close_camera()
            sys.exit(1)

    def __del__(self):
        self.auto_exposure_enable()
        self.auto_gain_enable()
        self.close_camera()
        print("The camera is closed")

    def close_camera(self):
        self.cam.EndAcquisition()
        self.cam.DeInit()
        self.cam = None
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def set_exposure_time(self, exposure_time):
        '''
            params:
                exposure_time: int -> time in terms of milliseconds
            return:
                result: Boolean ->
        '''
        try:
            exposure_time *= 1000.0
            result = True
            if self.cam.ExposureAuto.GetAccessMode() != spin.RW:
                print("Automatic exposure cannot be disabled")
                return False

            self.cam.ExposureAuto.SetValue(spin.ExposureAuto_Off)

            if self.cam.ExposureTime.GetAccessMode() != spin.RW:
                print("Exposure time cannot be set")
                self.auto_exposure_enable()
                return False

            if exposure_time < self.min_exposure_time:
                exposure_time = self.min_exposure_time
                print(f"Exposure time cannot be less than minimum exposure \
                        time ({self.min_exposure_time} us). \
                        It is set to the min value.")
            elif exposure_time > self.max_exposure_time:
                exposure_time = self.max_exposure_time
                print(f"Exposure time cannot be higher than maximum exposure \
                        time ({self.max_exposure_time} us). \
                        It is set to the min value.")
            self.cam.ExposureTime.SetValue(exposure_time)
            self.exposure_time = exposure_time / 1000.0
        except spin.SpinnakerException as ex:
            print(f"Error: {ex}")
            result = False
        return result

    def auto_exposure_enable(self):
        result = True
        try:
            if self.cam.ExposureAuto.GetAccessMode() != spin.RW:
                print("Automatic exposure cannot be enabled")
                return False
            self.cam.ExposureAuto.SetValue(spin.ExposureAuto_Continuous)
        except spin.SpinnakerException as ex:
            print(f"Error: {ex}")
            result = False
        return result

    def set_gain(self, gain):
        result = True
        try:
            if self.cam.GainAuto.GetAccessMode() != spin.RW:
                print("Automatic gain cannot be disabled")
                return False
            self.cam.GainAuto.SetValue(spin.GainAuto_Off)
            if self.cam.Gain.GetAccessMode() != spin.RW:
                print("Gain cannot be set")
                self.auto_gain_enable()
                return False
            if gain < self.min_gain:
                gain = self.min_gain
                print(f"Gain cannot be less than the minimum gain. It is set \
                      to the minimum value {self.min_gain}")
            elif gain > self.max_gain:
                gain = self.max_gain
                print(f"Gain cannot be higher than the maximum value. It is \
                      set to the maximum value {self.max_gain}")
            self.cam.Gain.SetValue(gain)
        except spin.SpinnakerException as ex:
            print(f'Error {ex}')
            result = False
        return result

    def auto_gain_enable(self):
        result = True
        try:
            if self.cam.Gain.GetAccessMode() != spin.RW:
                print("Automatic gain cannot be enabled")
                return False
            self.cam.Gain.SetValue(spin.GainAuto_Continuous)
        except spin.SpinnakerException as ex:
            print(f"Error: {ex}")
            result = False
        return result

    def read(self):
        result = True
        final_image = None
        timeout = int(self.exposure_time) + 1000
        try:
            image_result = self.cam.GetNextImage(timeout)
            if image_result.IsIncomplete():
                print("Incomplete Image")
                return False, final_image
            # image_converted = self.processor.Convert(image_result, /
            #                                          spin.PixelFormat_RGB8)
            # image_result.Save("test.jpg")

            final_image = image_result.GetNDArray()
            image_result.Release()
        except spin.SpinnakerException as ex:
            print(f"Error: {ex}")
            result = False
        return result, final_image
