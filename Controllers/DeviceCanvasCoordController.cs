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
public class DeviceCanvasCoordController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IMapper _mapper;

    public DeviceCanvasCoordController(AppDbContext context, IMapper mapper)
    {
        _context = context;
        _mapper = mapper;
    }

    // PUT: api/DeviceCanvasCoord/5
    // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
    [HttpPut("{id}")]
    public IActionResult PutDeviceCanvasCoord(int id, DeviceCanvasCoordDto deviceCanvasCoordDto)
    {
        var device = _context.Devices.SingleOrDefault(x => x.Id == id);

        if (device == null)
        {
            return NotFound();
        }

        device.X = deviceCanvasCoordDto.X;
        device.Y = deviceCanvasCoordDto.Y;

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

    private bool DeviceExists(int id)
    {
        return _context.Devices.Any(e => e.Id == id);
    }

}

