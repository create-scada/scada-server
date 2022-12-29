namespace Scada.Controllers;

using System.Collections.Generic;
using System.Linq;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Scada;
using Scada.Models;
using Scada.Dto;
using AutoMapper;

[Route("api/[controller]")]
[ApiController]
public class DevicesController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IMapper _mapper;

    public DevicesController(AppDbContext context, IMapper mapper)
    {
        _context = context;
        _mapper = mapper;
    }

    // GET: api/Devices
    [HttpGet]
    public ActionResult<IEnumerable<DeviceGetDto>> GetDevices(int locationId)
    {
        var devices = _context.Devices.Where(x => x.LocationId == locationId)
                                               .Include(x => x.DisplayPoints);

        var deviceDtos = new List<DeviceGetDto>();
        foreach (var device in devices)
        {
            deviceDtos.Add(_mapper.Map<DeviceGetDto>(device));
        }

        return Ok(deviceDtos);
    }

    // GET: api/Devices/5
    [HttpGet("{id}")]
    public ActionResult<DeviceGetDto> GetDevice(int id)
    {
        var device = _context.Devices.Include(x => x.DisplayPoints).SingleOrDefault(x => x.Id == id);

        if (device == null)
        {
            return NotFound();
        }

        DeviceGetDto deviceGetDto = _mapper.Map<DeviceGetDto>(device);

        return Ok(deviceGetDto);
    }

    // PUT: api/Device/5
    // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
    [HttpPut("{id}")]
    public IActionResult PutDevice(int id, DevicePostDto devicePostDto)
    {
        var device = _context.Devices.SingleOrDefault(x => x.Id == id);

        if (device == null)
        {
            return NotFound();
        }

        _context.Entry(device).State = EntityState.Modified;

        try
        {
            _context.SaveChanges();
        }
        catch (DbUpdateConcurrencyException)
        {
            if (!DeviceExists(id))
            {
                return NotFound();
            }
            else
            {
                throw;
            }
        }

        return NoContent();
    }

    // POST: api/Devices
    // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
    [HttpPost]
    public ActionResult<DevicePostDto> PostDevice(DevicePostDto devicePostDto)
    {
        Device device = _mapper.Map<Device>(devicePostDto);
        _context.Devices.Add(device);
        _context.SaveChanges();

        return CreatedAtAction("GetDevice", new { id = device.Id }, devicePostDto);
    }

    private bool DeviceExists(int id)
    {
        return _context.Devices.Any(e => e.Id == id);
    }

}

