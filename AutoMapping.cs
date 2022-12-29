namespace Scada;

using System.Text;
using AutoMapper;
using Scada.Dto;
using Scada.Models;

public class AutoMapping : Profile
{
    public AutoMapping()
    {
        //CreateMap<string, byte[]>().ConstructUsing(s => Encoding.UTF8.GetBytes(s));
        CreateMap<Location, LocationGetDto>();
        CreateMap<LocationPostDto, Location>();
        CreateMap<Device, DeviceGetDto>();
        CreateMap<DevicePostDto, Device>();
        CreateMap<DisplayPoint, DisplayPointGetDto>();
        CreateMap<DisplayPointPostDto, DisplayPoint>();
        CreateMap<Reading, ReadingGetDto>();
        CreateMap<ReadingPostDto, Reading>();
    }
}